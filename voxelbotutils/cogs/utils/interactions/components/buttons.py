import enum
import typing
import uuid

import discord

from .models import DisableableComponent, get_partial_emoji


class ButtonStyle(enum.IntEnum):
    """
    An enum of the available button styles.

    Attributes:
        PRIMARY: A blurple button.
        SECONDARY: A grey button.
        SUCCESS: A green button.
        DANGER: A red button.
        LINK: A button that navigates to a URL, and doesn't
            dispatch an interaction create payload.
    """

    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class Button(DisableableComponent):
    """
    A button as supported by the Discord UI.
    """

    __slots__ = ("label", "style", "custom_id", "emoji", "url", "disabled",)
    TYPE = 2
    WIDTH = 1

    def __init__(
            self, label: str = None, custom_id: str = None, *, style: ButtonStyle = ButtonStyle.PRIMARY,
            emoji: typing.Union[str, discord.PartialEmoji] = None,
            url: str = None, disabled: bool = False):
        """
        Args:
            label (str): The label that is added to the button.
            style (voxelbotutils.ButtonStyle, optional): The style that the button should use.
            custom_id (str, optional): The custom ID that should be assigned to the button. If you
                don't provide one, then a UUID1 is generated automatically. Buttons with the LINK
                style do not support the :attr:`custom_id` attribute, so it will be ignored.
            emoji (typing.Union[str, discord.PartialEmoji], optional): The emoji that should be
                added to the button.
            url (str, optional): The URL that the button points to. This is only supported when the
                LINK style is used.
            disabled (bool, optional): Whether or not the button is clickable.

        Raises:
            ValueError: If a URL is passed and the style isn't set to `ButtonStyle.LINK` or vice-vera,
                this will be raised.
        """

        self.label = label
        self.style = style
        self.custom_id = custom_id or str(uuid.uuid1())
        self.emoji = get_partial_emoji(emoji)
        self.url = url
        self.disabled = disabled
        if url is None and self.style == ButtonStyle.LINK:
            raise ValueError("Missing URL for button type of link")
        if url is not None and self.style != ButtonStyle.LINK:
            raise ValueError("Incompatible URL passed for button not of type link")
        if not label and not emoji:
            raise ValueError("Both label and emoji cannot be empty")

    def to_dict(self) -> dict:
        v = {
            "type": self.TYPE,
            "label": self.label,
            "style": self.style.value,
            "disabled": self.disabled,
        }
        if self.emoji:
            if isinstance(self.emoji, (discord.Emoji, discord.PartialEmoji)):
                v.update({
                    "emoji": {
                        "name": self.emoji.name,
                        "id": str(self.emoji.id) if self.emoji.id else None,
                        "animated": self.emoji.animated,
                    },
                })
            else:
                v.update({
                    "emoji": {
                        "name": self.emoji,
                    },
                })
        if self.url:
            v.update({"url": self.url})
        else:
            v.update({"custom_id": self.custom_id})
        return v

    @classmethod
    def from_dict(cls, data: dict) -> 'Button':
        """
        Construct an instance of a button from an API response.

        Args:
            data (dict): The payload data that the button should be constructed from.

        Returns:
            voxelbotutils.Button: The button that the payload describes.
        """

        emoji = data.get("emoji")
        if emoji is not None:
            emoji_id = emoji.get("id")
            if emoji_id is None:
                emoji = emoji.get("name")
            else:
                emoji = discord.PartialEmoji(
                    name=emoji.get("name"),
                    animated=emoji.get("animated", False),
                    id=emoji.get("id"),
                )
        return cls(
            label=data.get("label"),
            style=ButtonStyle(data.get("style", ButtonStyle.PRIMARY.value)),
            custom_id=data.get("custom_id"),
            emoji=emoji,
            disabled=data.get("disabled", False),
        )
