import discord

from .buttons import ButtonStyle, Button  # noqa
from .select_menu import SelectMenu, SelectOption  # noqa
from .models import BaseComponent, DisableableComponent, ComponentHolder # noqa
from .action_row import ActionRow, MessageComponents, component_types # noqa
from ..interaction_messageable import InteractionMessageable
from ...models import ComponentMessage


class ComponentInteractionPayload(InteractionMessageable):
    """
    An interaction messageable that comes from a component interaction.
    """

    __slots__ = ("component", "user", "message", "guild", "channel", "_state", "data",)
    ACK_IS_EDITABLE = False

    async def ack(self, *args, **kwargs):
        """:meta private:"""

        return await self.defer(*args, defer_type=6, **kwargs)

    async def defer_update(self):
        """
        Sends a deferred update payload to Discord for this interaction.
        """

        await self.defer(defer_type=6)

    async def update_message(self, *args, **kwargs):
        """
        Sends an update to the original message as an interaction response.
        """

        v = await self.message.edit(*args, wait=False, _no_wait_response_type=7, **kwargs)
        self._sent_ack_response = True
        self._sent_message_response = True
        return v

    @staticmethod
    def get_component_from_payload(components, search_id):
        """
        Get a component from the message payload given its custom ID.
        """

        for action_row in components:
            for component in action_row.get('components', list()):
                if component.get('custom_id', None) == search_id:
                    return component
        return None

    @classmethod
    def from_payload(cls, data, state):
        """
        Construct a response from the gateway payload.
        """

        # Try and find the component that was clicked
        clicked_button_id = data['data']['custom_id']
        clicked_button_payload = cls.get_component_from_payload(
            data['message'].get('components', list()),
            clicked_button_id,
        )

        # Get the component type that we want to reconstruct
        component_model = BaseComponent
        if clicked_button_payload:
            component_model = component_types.get(clicked_button_payload['type'], BaseComponent)

        # And reconstruct that model
        try:
            clicked_button_object = component_model.from_dict(clicked_button_payload)
        except NotImplementedError:
            clicked_button_object = BaseComponent()
            clicked_button_object.custom_id = clicked_button_id

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
            v.message = ComponentMessage(channel=channel, data=data['message'], state=state)
        except KeyError:
            v.message = discord.PartialMessage(channel=channel, id=int(data['message']['id']))
        if guild:
            v.user = discord.Member(data=data['member'], guild=guild, state=state)
        else:
            v.user = discord.User(data=data['user'], state=state)
        return v
