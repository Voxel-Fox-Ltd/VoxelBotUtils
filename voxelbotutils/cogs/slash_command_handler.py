import discord
from discord.ext import commands

from . import utils


class InteractionMessage(object):

    def __init__(self, guild, channel, author, content, state, data):
        self.guild = guild
        self.channel = channel
        self.author = author
        self._state = state
        self.content = content
        self.mentions = []
        self._handle_author(data['member']['user'])

    def _handle_author(self, author):
        self.author = self._state.store_user(author)
        if isinstance(self.guild, discord.Guild):
            found = self.guild.get_member(self.author.id)
            if found is not None:
                self.author = found


class InteractionContext(commands.Context):

    async def send(self, content, **kwargs):
        url = "https://discord.com/api/v8/interactions/{id}/{token}/callback".format(
            id=self._interaction_data["interaction_id"], token=self._interaction_data["token"],
        )
        headers = {
            "Authorization": f"Bot {self.bot.config['token']}",
        }
        json = {
            "type": 4,
            "data": {
                "content": content,
            },
        }
        try:
            v = await self.bot.session.post(url, json=json, headers=headers)
        except Exception as e:
            self.bot.logger.info(e)
        self.total_interaction_sends += 1
        self.bot.logger.info(await v.json())


class SlashCommandHandler(utils.Cog):

    async def get_context_from_interaction(self, payload, *, cls=InteractionContext):
        view = commands.view.StringView(f"<@{self.bot.user.id}> {payload['data']['name']} {' '.join([i['value'] for i in payload['data']['options']])}")
        fake_message = InteractionMessage(
            guild=self.bot.get_guild(int(payload['guild_id'])),
            channel=self.bot.get_channel(int(payload['channel_id'])),
            author=self.bot.get_guild(int(payload['guild_id'])),
            state=self.bot._get_state(),
            data=payload,
            content=view.buffer,
        )
        ctx = cls(prefix=None, view=view, bot=self.bot, message=fake_message)
        view.skip_string(f"<@{self.bot.user.id}> ")
        invoker = view.get_word()
        ctx.invoked_with = invoker
        ctx.prefix = f"<@{self.bot.user.id}> "
        ctx._interaction_data = {"token": payload["token"], "interaction_id": payload["id"], "command_id": payload["data"]["id"]}
        ctx.command = self.bot.all_commands.get(invoker)
        ctx.total_interaction_sends = 0
        return ctx

    @utils.Cog.listener()
    async def on_socket_response(self, payload):
        if payload['t'] != 'INTERACTION_CREATE':
            return
        self.logger.info("Received interaction payload %s" % (str(payload)))
        ctx = await self.get_context_from_interaction(payload['d'])
        self.logger.info("Received context object")
        await self.bot.invoke(ctx)
        self.logger.info("Invoked context object")

    @commands.command(cls=utils.Command)
    @commands.is_owner()
    async def addslashcommands(self, ctx):
        """
        Adds all of the bot's slash commands to the global interaction handler.
        """

        commands = list(self.bot.walk_commands())
        filtered_commands = self.bot.help_command.filter_commands_classmethod(ctx, commands)
        # make post request here idc


def setup(bot):
    x = SlashCommandHandler(bot)
    bot.add_cog(x)
