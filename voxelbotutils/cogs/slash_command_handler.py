import typing
import enum

import discord
from discord.ext import commands

from . import utils


class ApplicationCommandOptionType(enum.IntEnum):
    SUBCOMMAND = 1
    SUBCOMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


class ApplicationCommandOptionChoice(object):

    def __init__(self, name:str, value:typing.Any):
        self.name: str = name
        self.value: typing.Any = value

    @classmethod
    def from_data(cls, data:dict):
        return cls(data['name'], data['value'])

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


class ApplicationCommandOption(object):

    def __init__(self, name:str, type:ApplicationCommandOptionType, description:str, default:typing.Optional[str]=None, required:bool=True):
        self.name: str = name
        self.type: ApplicationCommandOptionType = type
        self.description: str = description
        self.default: typing.Any = default
        self.required: bool = required
        self.choices: typing.List[ApplicationCommandOptionChoice] = list()
        self.options: typing.List['ApplicationCommandOption'] = list()

    def add_choice(self, choice:ApplicationCommandOptionChoice) -> None:
        self.choices.append(choice)

    def add_option(self, option:'ApplicationCommandOption') -> None:
        self.options.append(option)

    @classmethod
    def from_data(cls, data:dict):
        base_option = cls(data['name'], ApplicationCommandOptionType(data['type']), data['description'], data.get('required', False))
        for choice in data['choices']:
            base_option.add_choice(ApplicationCommandOptionChoice.from_data(choice))
        for option in data['options']:
            base_option.add_option(cls.from_data(option))
        return base_option

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "default": self.default,
            "required": self.required,
            "choices": [i.to_json() for i in self.choices],
            "options": [i.to_json() for i in self.options],
        }


class ApplicationCommand(object):

    def __init__(self, name:str, description:str):
        self.name: str = name
        self.description: str = description
        self.options: typing.List[ApplicationCommandOption] = list()
        self.id: int = None
        self.application_id: int = None

    def add_option(self, option:ApplicationCommandOption):
        self.options.append(option)

    @classmethod
    def from_data(cls, data:dict):
        command = cls(data['name'], data['description'])
        command.id = int(data['id'])
        command.application_id = int(data['application_id'])
        for option in data['options']:
            command.add_option(ApplicationCommandOption.from_data(option))
        return command

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "options": [i.to_json() for i in self.options],
        }


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
        discord.User: ApplicationCommandOptionType.USER,
        discord.Member: ApplicationCommandOptionType.USER,
        discord.TextChannel: ApplicationCommandOptionType.CHANNEL,
        discord.Role: ApplicationCommandOptionType.ROLE,
        str: ApplicationCommandOptionType.STRING,
        int: ApplicationCommandOptionType.INTEGER,
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

    async def get_application_id(self):
        if self.application_id:
            return self.application_id
        app = await self.bot.application_info()
        self.application_id = app.id

    async def get_slash_commands(self):
        """
        Get the application's global command objects.
        """

        if self.commands is not None:
            return self.commands
        url = "https://discord.com/api/applications/{application_id}/commands".format(application_id=await self.get_application_id())
        headers = {"Authorization": f"Bot {self.bot.config['token']}"}
        site = await self.bot.session.get(url, headers=headers)
        data = await site.json()
        self.commands = [ApplicationCommand.from_data(i) for i in data]
        return self.commands

    @commands.command(cls=utils.Command)
    @commands.is_owner()
    async def addslashcommands(self, ctx):
        """
        Adds all of the bot's slash commands to the global interaction handler.
        """

        commands_we_cant_deal_with = []
        commands = list(self.bot.walk_commands())
        filtered_commands = await self.bot.help_command.filter_commands_classmethod(ctx, commands)
        for command in filtered_commands:
            for arg in command.clean_params.values():
                if arg.annotation in self.COMMAND_TYPE_MAPPER:
                    continue
                if self.is_typing_optional(arg.annotation) and self.get_non_optional_type(arg.annotation) in self.COMMAND_TYPE_MAPPER:
                    continue
                commands_we_cant_deal_with.append(command.name + " " + str(command.clean_params.values()))
                break
        if commands_we_cant_deal_with:
            return await ctx.send("\n".join(commands_we_cant_deal_with))
        return await ctx.send("I can deal with all of these.")


def setup(bot):
    x = SlashCommandHandler(bot)
    bot.add_cog(x)
