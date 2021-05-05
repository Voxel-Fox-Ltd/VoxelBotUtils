import discord

from .models import BaseComponent, DisableableComponent, ComponentHolder, MessageComponents, ActionRow
from .buttons import ButtonStyle, Button
from ..interaction_messageable import InteractionMessageable


class ComponentInteractionPayload(InteractionMessageable):
    """
    An interaction messageable that comes from a component interaction.
    """

    __slots__ = ("component", "user", "message", "guild", "channel", "_state", "data")
    ACK_RESPONSE_TYPE = 6
    ACK_IS_EDITABLE = False
    IS_COMPONENT = True

    @classmethod
    def from_payload(cls, data, state):
        """
        Construct a response from the gateway payload.
        """

        # Reconstruct the component that was clicked
        clicked_button_id = data['data']['custom_id']
        clicked_button_payload = None
        for action_row in data['message']['components']:
            for component in action_row['components']:
                if component['custom_id'] == clicked_button_id:
                    clicked_button_payload = component
                    break
            if clicked_button_payload is not None:
                break

        # TODO make this into something more abstract than Button so the code doesn't
        # need to be changed all too much for other types of interactions.
        # I'm pretty sure that I need only reconstruct the custom ID or value?? depending
        # on what the other components use, but this works for now, while Buttons are the
        # only interaction.
        clicked_button_object = Button.from_dict(clicked_button_payload)

        # Make the response
        v = cls()
        v.data = data
        v._state = state
        v.component = clicked_button_object
        channel, guild = state._get_guild_channel(data)
        v.channel = channel
        v.guild = guild
        v.message = discord.Message(channel=channel, data=data['message'], state=state)
        if guild:
            v.user = discord.Member(data=data['member'], guild=guild, state=state)
        else:
            v.user = discord.User(data=data['user'], state=state)
        return v
