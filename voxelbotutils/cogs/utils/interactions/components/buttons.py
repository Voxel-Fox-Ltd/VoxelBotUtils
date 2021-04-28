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


class ButtonInteractionPayload(object):

    __slots__ = ("button", "user_id", "message_id", "guild_id", "channel_id",)

    @classmethod
    def from_payload(cls, data):
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
        v.button = clicked_button_object
        v.user_id = int(data['member']['user']['id'])
        v.channel_id = int(data['channel_id'])
        v.guild_id = int(data['guild_id'])
        v.message_id = int(data['message']['id'])
        return v
