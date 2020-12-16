import enum
import typing


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
        for option in data.get('options', list()):
            command.add_option(ApplicationCommandOption.from_data(option))
        return command

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "options": [i.to_json() for i in self.options],
        }
