import enum
import typing
import uuid
import asyncio
import re

import discord

from .models import DisableableComponent
from ..interaction_messageable import InteractionMessageable


class ButtonStyle(enum.IntEnum):
    PRIMARY = 1  # A blurple button
    SECONDARY = 2  # A grey button
    SUCCESS = 3  # A green button
    DANGER = 4  # A red button
    LINK = 5  # A button that navigates to a URL


class Button(DisableableComponent):
    """
    A Discord UI button.
    """

    __slots__ = ("label", "style", "custom_id", "emoji", "url", "disabled",)

    def __init__(
            self, label: str, style: ButtonStyle = ButtonStyle.PRIMARY, custom_id: str = None,
            emoji: typing.Union[str, discord.PartialEmoji] = None,
            url: str = None, disabled: bool = False):
        """
        Args:
            label (str): The label that is added to the button.
            style (ButtonStyle, optional): The style that the button should use.
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
        self.emoji = emoji
        if isinstance(emoji, str):
            match = re.match(r'<(a?):([a-zA-Z0-9\_]+):([0-9]+)>$', emoji)
            if match:
                emoji_animated = bool(match.group(1))
                emoji_name = match.group(2)
                emoji_id = int(match.group(3))
                self.emoji = discord.PartialEmoji(
                    name=emoji_name,
                    animated=emoji_animated,
                    id=emoji_id,
                )
        self.url = url
        self.disabled = disabled
        if url is None and self.style == ButtonStyle.LINK:
            raise ValueError("Missing URL for button type of link")
        if url is not None and self.style != ButtonStyle.LINK:
            raise ValueError("Incompatible URL passed for button not of type link")

    def to_dict(self) -> dict:
        v = {
            "type": 2,
            "label": self.label,
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
            Button: The button that the payload describes.
        """

        emoji = data.get("emoji")
        if emoji is not None:
            emoji = discord.PartialEmoji(
                name=emoji.get("name"),
                animated=emoji.get("animated", False),
                id=emoji.get("id"),
            )
        return cls(
            label=data.get("label"),
            style=ButtonStyle(data.get("style")),
            custom_id=data.get("custom_id"),
            emoji=emoji,
        )


class ButtonInteractionPayload(InteractionMessageable):
    """
    An interaction messageable that comes from a button interaction.
    """

    __slots__ = ("button", "user", "message", "guild", "channel", "_state", "data")
    ACK_RESPONSE_TYPE = 6
    ACK_IS_EDITABLE = False
    IS_COMPONENT = True

    @classmethod
    def from_payload(cls, data, state):
        """
        Construct a response from the gateway payload.
        """

        # Reconstruct the button that was clicked
        clicked_button_id = data['data']['custom_id']
        clicked_button_payload = None
        for action_row in data['message']['components']:
            for button in action_row['components']:
                if button['custom_id'] == clicked_button_id:
                    clicked_button_payload = button
                    break
            if clicked_button_payload is not None:
                break
        clicked_button_object = Button.from_dict(clicked_button_payload)

        # Make the response
        v = cls()
        v.data = data
        v._state = state
        v.button = clicked_button_object
        channel, guild = state._get_guild_channel(data)
        v.channel = channel
        v.guild = guild
        v.message = discord.Message(channel=channel, data=data['message'], state=state)
        if guild:
            v.user = discord.Member(data=data['member'], guild=guild, state=state)
        else:
            v.user = discord.User(data=data['user'], state=state)
        return v
