import discord

from .models import BaseComponent, DisableableComponent, ComponentHolder
from .action_row import MessageComponents, ActionRow, component_types
from .buttons import ButtonStyle, Button
from .select_menu import SelectOption, SelectMenu
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

        # Try and find the component that was clicked
        clicked_button_id = data['data']['custom_id']
        clicked_button_payload = None
        for action_row in data['message'].get('components', list()):
            for component in action_row.get('components', list()):
                if component.get('custom_id', None) == clicked_button_id:
                    clicked_button_payload = component
                    break
            if clicked_button_payload is not None:
                break

        # Get the component type that we want to reconstruct
        clicked_button_type = BaseComponent
        if clicked_button_payload:
            component_model = component_types.get(clicked_button_payload['type'], BaseComponent)

        # And reconstruct that model
        if clicked_button_type == BaseComponent:
            clicked_button_object = BaseComponent()
            clicked_button_object.custom_id = clicked_button_id
        else:
            clicked_button_object = clicked_button_type.from_dict(clicked_button_payload)

        # Make the response
        v = cls()
        v.data = data  # The raw gateway data
        v.component = clicked_button_object  # The component that was interacted with
        v.values = data['data'].get("values", list())  # The values that were sent through with the payload
        v._state = state
        channel, guild = state._get_guild_channel(data)
        v.channel = channel
        v.guild = guild
        try:
            v.message = discord.Message(channel=channel, data=data['message'], state=state)
        except KeyError:
            v.message = discord.PartialMessage(channel=channel, id=int(data['message']['id']))
        if guild:
            v.user = discord.Member(data=data['member'], guild=guild, state=state)
        else:
            v.user = discord.User(data=data['user'], state=state)
        return v
