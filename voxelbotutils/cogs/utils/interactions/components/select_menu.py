import typing

import discord

from .models import BaseComponent, get_partial_emoji


class SelectOption(BaseComponent):
    """
    An option menu that can go into a :class:`voxelbotutils.SelectMenu` object.
    """

    def __init__(
            self, label: str, value: str, *, description: str = None,
            emoji: typing.Union[str, discord.PartialEmoji] = None, default: bool = None):
        """
        Args:
            label (str): The label that gets shown on the option.
            value (str): The value that this option will give back to the bot.
            description (str, optional): A description for the option.
            emoji (typing.Union[str, discord.PartialEmoji], optional): An emoji to be displayed with the option.
            default (bool, optional): Whether or not the option is selected by default.
        """

        self.label = label
        self.value = value
        self.description = description
        self.emoji = get_partial_emoji(emoji)
        self.default = default or False

    def to_dict(self) -> dict:
        v = {
            "label": self.label,
            "value": self.value,
        }
        if self.description:
            v.update({"description": self.description})
        if self.emoji:
            if isinstance(self.emoji, (discord.Emoji, discord.PartialEmoji)):
                v.update({
                    "emoji": {
                        "name": self.emoji.name,
                        "id": str(self.emoji.id),
                        "animated": self.emoji.animated,
                    },
                })
            else:
                v.update({
                    "emoji": {
                        "name": self.emoji,
                    },
                })
        if self.default:
            v.update({"default": self.default})
        return v

    @classmethod
    def from_dict(cls, data: dict):
        emoji = data.get("emoji")
        if emoji is not None:
            emoji = discord.PartialEmoji(
                name=emoji.get("name"),
                animated=emoji.get("animated", False),
                id=emoji.get("id"),
            )
        return cls(
            label=data.get("label"),
            value=data.get("value"),
            description=data.get("description"),
            emoji=emoji,
            default=data.get("default", False),
        )


class SelectMenu(BaseComponent):
    """
    Discord's dropdown component.
    """

    TYPE = 3
    WIDTH = 5

    def __init__(
            self, custom_id: str, options: typing.List[SelectOption], placeholder: str = None,
            min_values: int = None, max_values: int = None):
        """
        Args:
            custom_id (str): The custom ID for this component.
            options (typing.List[SelectOption]): The options that should be displayed in this component.
            placeholder (str, optional): The placeholder text for when nothing is selected.
            min_values (int, optional): The minimum amount of selectable values.
            max_values (int, optional): The maximum amount of selectable values.
        """

        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values or 1
        self.max_values = max_values or 1

    def to_dict(self):
        return {
            "type": self.TYPE,
            "custom_id": self.custom_id,
            "placeholder": self.placeholder,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "options": [i.to_dict() for i in self.options],
        }

    @classmethod
    def from_dict(cls, data: dict):
        v = data.get("options")
        options = [SelectOption.from_dict(i) for i in v]
        return cls(
            custom_id=data.get("custom_id"),
            options=options,
            placeholder=data.get("placeholder"),
            min_values=data.get("min_values"),
            max_values=data.get("max_values"),
        )
