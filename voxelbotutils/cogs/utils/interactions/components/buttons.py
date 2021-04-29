import enum
import typing
import uuid

import discord

from ..interaction_messageable import InteractionMessageable


class ButtonStyle(enum.IntEnum):
    PRIMARY = 1  # A blurple button
    SECONDARY = 2  # A grey button
    SUCCESS = 3  # A green button
    DANGER = 4  # A red button
    LINK = 5  # A button that navigates to a URL


class Button(object):

    __slots__ = ("label", "style", "custom_id", "emoji", "url", "disabled",)

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
    def from_dict(cls, data):
        """
        Construct an instance of a button from an API response.
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

    __slots__ = ("button", "user", "message", "guild", "channel", "_state", "data")

    async def _get_channel(self):
        """
        Get the (id, token) pair that's used to send to the webhook necessary.
        """

        return (self._state.application_id, self.data['token'],)

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
            # v.user = discord.User(data=data['member']['user'], state=state)
            raise Exception("Cannot create a button payload from DMs")
        return v
