import typing
import enum
import io
import json

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
    async def send(self, *args, **kwargs):
        return await self._interaction_webhook.send(*args, wait=True, **kwargs)


class SlashCommandHandler(utils.Cog):

    COMMAND_TYPE_MAPPER = {
        discord.User: utils.interactions.ApplicationCommandOptionType.USER,
        discord.Member: utils.interactions.ApplicationCommandOptionType.USER,
        discord.TextChannel: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        discord.VoiceChannel: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        discord.CategoryChannel: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        discord.Role: utils.interactions.ApplicationCommandOptionType.ROLE,
        str: utils.interactions.ApplicationCommandOptionType.STRING,
        int: utils.interactions.ApplicationCommandOptionType.INTEGER,
        utils.converters.UserID: utils.interactions.ApplicationCommandOptionType.USER,
        utils.converters.ChannelID: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        utils.converters.EnumConverter: utils.interactions.ApplicationCommandOptionType.STRING,
        utils.converters.BooleanConverter: utils.interactions.ApplicationCommandOptionType.BOOLEAN,
        utils.converters.ColourConverter: utils.interactions.ApplicationCommandOptionType.STRING,
        utils.converters.FilteredUser: utils.interactions.ApplicationCommandOptionType.USER,
        utils.converters.FilteredMember: utils.interactions.ApplicationCommandOptionType.USER,
    }

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.commands: typing.List[ApplicationCommand] = None
        self.application_id = None

    async def get_context_from_interaction(self, payload, *, cls=InteractionContext):
        # Make a context
        view = commands.view.StringView(f"<@{self.bot.user.id}> {payload['data']['name']} {' '.join([i['value'] for i in payload['data']['options']])}")
        fake_message = InteractionMessage(
            guild=self.bot.get_guild(int(payload['guild_id'])),
            channel=self.bot.get_channel(int(payload['channel_id'])),
            author=self.bot.get_guild(int(payload['guild_id'])),
            state=self.bot._get_state(),
            data=payload,
            content=view.buffer,
        )
        ctx = cls(prefix=f"<@{self.bot.user.id}> ", view=view, bot=self.bot, message=fake_message)
        ctx.is_slash_command = True
        view.skip_string(f"<@{self.bot.user.id}> ")
        invoker = view.get_word()

        # Make it work
        ctx.invoked_with = invoker
        ctx._interaction_webhook = discord.Webhook.partial(
            await self.get_application_id(), payload["token"],
            adapter=discord.AsyncWebhookAdapter(self.bot.session)
        )
        ctx.command = self.bot.all_commands.get(invoker)

        # Send async data response
        url = "https://discord.com/api/v8/interactions/{id}/{token}/callback".format(id=payload["id"], token=payload["token"])
        await self.bot.session.post(url, json={"type": 5}, headers={"Authorization": f"Bot {self.bot.config['token']}"})

        # Return context
        return ctx

    @utils.Cog.listener()
    async def on_socket_response(self, payload):
        if payload['t'] != 'INTERACTION_CREATE':
            return
        self.logger.info("Received interaction payload %s" % (str(payload)))
        ctx = await self.get_context_from_interaction(payload['d'])
        await self.bot.invoke(ctx)

    @staticmethod
    def is_typing_optional(annotation):
        """
        Stolen from Rapptz - https://github.com/Rapptz/discord.py/blob/60f804c63298d5f46a5ae4352b049d91b16d1b8c/discord/ext/commands/core.py#L975-L984
        """

        if annotation.default is None:
            return True
        try:
            origin = annotation.__origin__
        except AttributeError:
            return False
        if origin is not typing.Union:
            return False
        if len(annotation.__args__) != 2:
            return False
        return annotation.__args__[-1] is type(None)

    @staticmethod
    def get_non_optional_type(annotation):
        return annotation.__args__[0]

    async def get_slash_commands(self):
        """
        Get the application's global command objects.
        """

        if self.commands is not None:
            return self.commands
        url = "https://discord.com/api/applications/{application_id}/commands".format(application_id=await self.bot.get_application_id())
        headers = {"Authorization": f"Bot {self.bot.config['token']}"}
        site = await self.bot.session.get(url, headers=headers)
        data = await site.json()
        self.commands = [ApplicationCommand.from_data(i) for i in data]
        return self.commands

    async def convert_into_application_command(self, ctx, command:typing.Union[utils.Command, utils.Group]) -> utils.interactions.ApplicationCommand:
        """
        Convert a given Discord command into an application command.
        """

        # Make command
        application_command = utils.interactions.ApplicationCommand(
            name=command.name,
            description=command.brief,
        )

        # Go through its args
        for arg in command.clean_params.values():
            arg_type = None
            required = True
            if arg.annotation in self.COMMAND_TYPE_MAPPER:
                arg_type = arg.annotation
            if self.is_typing_optional(arg.annotation) and self.get_non_optional_type(arg.annotation) in self.COMMAND_TYPE_MAPPER:
                arg_type = self.get_non_optional_type(arg.annotation)
                required = False
            if arg_type is None:
                raise Exception("Couldn't add a convert into a slash command wew")
            safe_arg_type = self.COMMAND_TYPE_MAPPER[arg_type]
            application_command.add_option(utils.interactions.ApplicationCommandOption(
                name=arg.name,
                description=None,
                type=safe_arg_type,
                required=required
            ))

        # Go through its subcommands
        if isinstance(command, utils.Group):
            subcommands = list(command.walk_commands())
            valid_subcommands = await self.bot.help_command.filter_commands_classmethod(ctx, valid_subcommands)
            for subcommand in valid_subcommands:
                application_command.add_option(self.convert_into_application_command(subcommand))

        # Return command
        return application_command

    async def convert_all_into_application_command(self, ctx):
        slash_commands = []
        commands = list(ctx.bot.walk_commands())
        filtered_commands = await self.bot.help_command.filter_commands_classmethod(ctx, commands)
        for command in filtered_commands:
            slash_commands.append(await self.convert_into_application_command(command))
        return slash_commands

    @commands.command(cls=utils.Command)
    @commands.is_owner()
    async def addslashcommands(self, ctx):
        """
        Adds all of the bot's slash commands to the global interaction handler.
        """

        x = await self.convert_all_into_application_command(ctx)
        await ctx.send(file=discord.File(io.StringIO(json.dumps([i.to_json() for i in x], indent=4)), filename="pain.json"))


def setup(bot):
    x = SlashCommandHandler(bot)
    bot.add_cog(x)
