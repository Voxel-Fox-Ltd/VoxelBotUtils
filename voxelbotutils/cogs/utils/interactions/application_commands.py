import enum
import typing

import discord


class ApplicationCommandOptionType(enum.IntEnum):
    """
    The different types of option that an application command argument can have.
    """

    SUBCOMMAND = 1  #: If the option is a subcommand.
    SUBCOMMAND_GROUP = 2  #: If the option is a subcommand group.
    STRING = 3  #: If the option is a string.
    INTEGER = 4  #: If the option is an integer.
    BOOLEAN = 5  #: If the option is a boolean.
    USER = 6  #: If the option is a user.
    CHANNEL = 7  #: If the option is a channel.
    ROLE = 8  #: If the option is a role.
    MENTIONABLE = 9  #: Any mentionable user or role.
    NUMBER = 10  #: Any double.


class ApplicationCommandType(enum.IntEnum):
    """
    The different types of application commands.
    """

    CHAT_INPUT = 1  #: Chat input application commands, like slash commands.
    USER = 2  #: An application command in the user context menu.
    MESSAGE = 3  #: An application command in the message context menu.


class ApplicationCommandOptionChoice(object):
    """
    The possible choices that an application command can take.

    Attributes:
        name (str): The name of this option.
        value (str): The value given to this option.
    """

    def __init__(self, name: str, value: typing.Any):
        """
        Args:
            name (str): The name of this option.
            value (typing.Any): The value given to this option.
        """

        self.name: str = name
        self.value: typing.Any = value

    @classmethod
    def from_data(cls, data: dict):
        return cls(data['name'], data['value'])

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


class ApplicationCommandOption(object):
    """
    An option displayed in a given application command.

    Attributes:
        name (str): The name of this option.
        type (ApplicationCommandOptionType): The type of this command option.
        description (str): The description given to this argument.
        default (typing.Any): The default value given to the command option.
        required (bool): Whether or not this option is required for the command to run.
        choices (typing.List[ApplicationCommandOptionChoice]): A list of choices that this command can take.
        options (typing.List[ApplicationCommandOption]): A list of options that go into the application command.
    """

    def __init__(
            self, name: str, type: ApplicationCommandOptionType, description: str,
            default: typing.Optional[str] = None, required: bool = True):
        """
        Args:
            name (str): The name of this option.
            type (ApplicationCommandOptionType): The type of this command option.
            description (str): The description given to this argument.
            default (typing.Any): The default value given to the command option.
            required (bool): Whether or not this option is required for the command to run.
        """

        self.name: str = name
        self.type: ApplicationCommandOptionType = type
        self.description: str = description
        self.default: typing.Any = default
        self.required: bool = required
        self.choices: typing.List[ApplicationCommandOptionChoice] = list()
        self.options: typing.List['ApplicationCommandOption'] = list()

    def add_choice(self, choice: ApplicationCommandOptionChoice) -> None:
        """
        Add a choice to this instance.
        """

        self.choices.append(choice)

    def add_option(self, option: 'ApplicationCommandOption') -> None:
        """
        Add an option to this instance.
        """

        self.options.append(option)

    @classmethod
    def from_data(cls, data: dict):
        base_option = cls(data['name'], ApplicationCommandOptionType(data['type']), data['description'], data.get('required', False))
        for choice in data.get('choices', list()):
            base_option.add_choice(ApplicationCommandOptionChoice.from_data(choice))
        for option in data.get('options', list()):
            base_option.add_option(cls.from_data(option))
        return base_option

    def to_json(self) -> dict:
        payload = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "default": self.default,
            "required": self.required,
            "choices": [i.to_json() for i in self.choices],
            "options": [i.to_json() for i in self.options],
        }
        if self.type in [ApplicationCommandOptionType.SUBCOMMAND, ApplicationCommandOptionType.SUBCOMMAND_GROUP]:
            payload.pop("required")
            payload.pop("default")
            payload.pop("choices")
        return payload


class ApplicationCommand(object):
    """
    An instance of an application command.

    Attributes:
        name (str): The name of this command.
        description (str): The description for this command.
        options (typing.List[ApplicationCommandOption]): A list of the options added to this command.
        id (int): The ID of this application command.
        application_id (int): The application ID that this command is attached to.
    """

    def __init__(self, name: str, description: str = None, type: ApplicationCommandType = ApplicationCommandType.CHAT_INPUT):
        """
        Args:
            name (str): The name of this command.
            description (str): The description for this command.
        """

        self.name: str = name
        self.description: str = description
        self.type: ApplicationCommandType = type
        self.options: typing.List[ApplicationCommandOption] = list()
        self.id: int = None
        self.application_id: int = None

    def __repr__(self):
        return f"ApplcationCommand<name={self.name}, type={self.type.name}>"

    def add_option(self, option: ApplicationCommandOption):
        """
        Add an option to this command instance.
        """

        self.options.append(option)

    @classmethod
    def from_data(cls, data: dict):
        command = cls(data['name'], data.get('description'), ApplicationCommandType(data.get('type', 1)))
        command.id = int(data.get('id', 0)) or None
        command.application_id = int(data.get('application_id', 0)) or None
        for option in data.get('options', list()):
            command.add_option(ApplicationCommandOption.from_data(option))
        return command

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.to_json() == other.to_json()

    def to_json(self):
        v = {
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "options": [i.to_json() for i in self.options],
        }
        if self.description is None:
            v.pop("description", None)
        if self.type != ApplicationCommandType.CHAT_INPUT:
            v.pop("options", None)
        return v


class InteractionMessage(discord.Message):

    def __init__(self, *, state, channel, data, content):
        self._state = state
        self.id = int(data['id'])
        self.webhook_id = None
        self.reactions = []
        self.attachments = []
        self.embeds = []
        self.application = None
        self.activity = None
        self.channel = channel
        self._edited_timestamp = None
        self.type = discord.MessageType.default
        self.pinned = False
        self.flags = discord.MessageFlags._from_value(0)
        self.mention_everyone = False
        self.tts = False
        self.content = content
        self.nonce = data.get('nonce')
        self.stickers = []
        self.reference = None
        self.mentions = []

        try:
            self._handle_author(data['member']['user'])
            self._handle_member(data['member'])
        except KeyError:
            self._handle_author(data['user'])
        try:
            self._handle_resolved(data['resolved'])
        except KeyError:
            pass

    def _handle_resolved(self, data):
        mentions = []
        try:
            for uid, payload in data['users']:
                user_payload = payload.copy()
                try:
                    user_payload.update({'member': data['members'][uid]})
                except KeyError:
                    pass
                mentions.append(user_payload)
        except KeyError:
            pass
        self._handle_mentions(mentions)
        self._handle_mention_roles(data.get('roles', {}))

    def _handle_mention_roles(self, role_mentions):
        self.role_mentions = []
        for _, payload in role_mentions.items():
            payload.update({"permissions_new": payload.get("permissions", 0)})
            r = discord.Role(guild=self.guild, state=self._state, data=payload)
            self.role_mentions.append(r)
