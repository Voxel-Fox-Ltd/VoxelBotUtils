import enum
import typing
import uuid

import discord


class ButtonStyle(enum.IntEnum):
    PRIMARY = 1  # A blurple button
    SECONDARY = 2  # A grey button
    SUCCEESS = 3  # A green button
    DANGER = 4  # A red button
    LINK = 5  # A button that navigates to a URL


class Button(object):

    def __init__(
            self, label: str, style: ButtonStyle = ButtonStyle.PRIMARY, custom_id: str = None,
            emoji: typing.Union[str, discord.PartialEmoji] = None,
            url: str = None, disabled: bool = False):
        self.label = label
        self.style = style
        self.custom_id = custom_id or str(uuid.uuid1())
        self.emoji = emoji
        self.url = url
        self.disabled = disabled
        if url is None and self.style == ButtonStyle.LINK:
            raise ValueError("Missing URL for button type of link")
        if url is not None and self.style != ButtonStyle.LINK:
            raise ValueError("Incompatible URL passed for button not of type link")

    def to_dict(self) -> dict:
        """
        Convert the current button into an API-friendly dict
        """

        v = {
            "type": 2,
            "label": self.label,
            "custom_id": self.custom_id,
            "style": self.style.value,
            "disabled": self.disabled,
        }
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
        if self.url:
            v.update({"url": self.url})
        return v
