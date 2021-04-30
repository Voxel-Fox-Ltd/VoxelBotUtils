import discord
from discord.ext import commands

from . import utils


class SlashCommandContext(utils.interactions.interaction_messageable.InteractionMessageable, utils.Context):

    def __init__(self, *args, **kwargs):
        super(utils.Context).__init__(*args, **kwargs)


class InteractionHandler(utils.Cog):

    async def get_context_from_interaction(self, payload, *, cls=SlashCommandContext):
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
        ctx.data = payload
        ctx.is_slash_command = True
        ctx.original_author_id = member.id
        view.skip_string(ctx.prefix)
        invoker = view.get_word()

        # Make it work
        ctx.invoked_with = invoker
        ctx.command = self.bot.all_commands.get(invoker)

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
            ctx._send_interaction_response_callback()
            await self.bot.invoke(ctx)
            return

        # See if it was a clicked component
        elif payload['d']['type'] == 3:
            clicked_button_payload = utils.interactions.components.ButtonInteractionPayload.from_payload(
                payload['d'], self.bot._connection,
            )
            clicked_button_payload._send_interaction_response_callback()
            self.bot.dispatch("button_click", clicked_button_payload)
            return

        # Something that we're unable to handle
        else:
            self.logger.warning("Invalid interaction type received - %d" % (payload['d']['type']))


def setup(bot:utils.Bot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
