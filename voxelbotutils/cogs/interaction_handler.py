import discord
from discord.ext import commands

from . import utils


class InteractionHandler(utils.Cog):

    async def get_context_from_interaction(self, payload, *, cls=utils.Context):
        """
        Make a context object from an interaction.
        """

        # Make a string view
        view = commands.view.StringView(
            f"<@{self.bot.user.id}> {payload['data']['name']} {' '.join([i['value'] for i in payload['data'].get('options', list())])}"
        )
        self.logger.debug(f"Made up fake string for interaction command: {view.buffer}")

        # Get some objects we can use to make the interaction message
        guild = self.bot.get_guild(int(payload['guild_id']))
        channel = self.bot.get_channel(int(payload['channel_id']))
        member_data = payload['member']
        member = discord.Member(data=member_data, guild=guild, state=self.bot._connection)

        # Make our fake message
        fake_message = utils.interactions.InteractionMessage(
            guild=guild,
            channel=channel,
            author=member,
            state=self.bot._connection,
            data=payload,
            content=view.buffer,
        )
        ctx = cls(prefix=f"<@{self.bot.user.id}> ", view=view, bot=self.bot, message=fake_message)
        ctx.is_slash_command = True
        ctx.original_author_id = member.id
        view.skip_string(ctx.prefix)
        invoker = view.get_word()

        # Make it work
        ctx.invoked_with = invoker
        adapter = discord.AsyncWebhookAdapter(self.bot.session)
        webhook = discord.Webhook.partial(
            await self.bot.get_application_id(), payload["token"],
            adapter=adapter,
        )
        webhook._state = self.bot._connection
        webhook.channel_id = int(payload['channel_id'])
        webhook.guild_id = int(payload['guild_id'])
        ctx._interaction_webhook = webhook
        ctx.command = self.bot.all_commands.get(invoker)

        # Send async data response
        async def send_callback():
            self.logger.debug("Posting type 5 response for interaction command %s." % (str(payload)))
            url = "https://discord.com/api/v8/interactions/{id}/{token}/callback".format(
                id=payload["id"], token=payload["token"],
            )
            return await self.bot.session.post(
                url, json={"type": 5},
                headers={"Authorization": f"Bot {self.bot.config['token']}"},
            )
        callback_task = self.bot.loop.create_task(send_callback())
        ctx._send_interaction_response_task = callback_task

        # Return context
        return ctx

    @utils.Cog.listener()
    async def on_socket_response(self, payload:dict):
        """
        Process any interaction create payloads we may receive.
        """

        if payload['t'] != 'INTERACTION_CREATE':
            return
        self.logger.debug("Received interaction payload %s" % (str(payload)))

        # See if it's a ping - it should _never_ be a ping, but let's put it here anyway
        if payload['d']['type'] == 1:
            return

        # See if it's a slash command
        elif payload['d']['type'] == 2:
            ctx = await self.get_context_from_interaction(payload['d'])
            if ctx.command:
                self.logger.debug("Invoking interaction context for command %s" % (ctx.command.name))
            await self.bot.invoke(ctx)
            return

        # See if it was a clicked component
        elif payload['d']['type'] == 3:
            async def send_callback():
                self.logger.debug("Posting type 5 response for button click %s." % (str(payload)))
                url = "https://discord.com/api/v8/interactions/{id}/{token}/callback".format(
                    id=payload["id"], token=payload["token"],
                )
                return await self.bot.session.post(
                    url, json={"type": 6},
                    headers={"Authorization": f"Bot {self.bot.config['token']}"},
                )
            callback_task = self.bot.loop.create_task(send_callback())
            clicked_button_payload = utils.interactions.components.ButtonInteractionPayload.from_payload(payload['d'])
            self.bot.dispatch("button_click", clicked_button_payload)
            return

        # Something that we're unable to handle
        else:
            self.logger.warning("Invalid interaction type received - %d" % (payload['d']['type']))


def setup(bot:utils.Bot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
