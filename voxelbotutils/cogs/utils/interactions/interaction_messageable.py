import asyncio
import collections

import discord
from discord.abc import Messageable, Typing


FakeResponse = collections.namedtuple("FakeResponse", ["status", "reason"])


class InteractionTyping(Typing):

    async def __aenter__(self):
        return self.__enter__()

    async def do_typing(self, sleep_forever: bool = True):
        if not self.messageable._sent_ack_response and not self.messageable._sent_message_response:
            async with self.messageable._send_interaction_response_lock:
                await self.messageable.ack()
        while sleep_forever:
            await asyncio.sleep(5)  # Loop forever


class InteractionMessageable(Messageable):
    """
    A messageable that allows you to send back responses to interaction payloads
    more easily.

    .. note::

        The interaciton messageable's send method also implements :code:`ephemeral` as a valid kwarg,
        but for ease of documentation, the send method remains undocumented, as aside from this it is
        unchanged from the rest of the messageable objects.

    Attributes:
        component (typing.Optional[BaseComponent]): The component that triggered this interaction.
            It may be none if the interaction that triggered this wasn't a component, such as when
            slash commands are used.
    """

    IS_INTERACTION = True
    IS_COMPONENT = False
    CAN_SEND_EPHEMERAL = True
    ACK_IS_EDITABLE = True
    ACK_RESPONSE_TYPE = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._send_interaction_response_lock = asyncio.Lock()  # A lock so we don't try to respond initially twice
        self._send_interaction_response_task = None  # The task for sending an initial "waiting" response
        self._sent_ack_response = False
        self._sent_message_response = False

        self.component = None  # We'll put the interacted-with component here if we get one

        # If we want to respond before sending a pending response, we can use type 4 - this responds intially with a message.
        #     After doing this we want to respond using webhooks rather than the interaction endpoint.
        # While pending we can send a type 5 response - this means that the interaction gets an ack and goes into a pending state.
        #     After doing this the first time we want to send an initial response again, and followup messages go to the webhook
        #     response endpoint.
        # Buttons have the luxury of a type 6 response - an ack response that doesn't tell the user we're waiting.
        #     Button responses can go immediately to the webhook response endpoint after this ack is received.

    async def _get_channel(self):
        """
        Get the (interaction_id, application_id, token) tuple that's used to send to the webhook necessary.
        """

        await self._wait_until_interaction_sent()
        return (self.data['id'], self._state.application_id, self.data['token'],)

    def _send_interaction_response_callback(self):
        """
        Send the original interaction response
        """

        async def send_callback():
            await asyncio.sleep(2)
            try:
                await self.trigger_typing()
            except Exception:
                pass
        self._send_interaction_response_task = self._state.loop.create_task(send_callback())

    async def _wait_until_interaction_sent(self):
        """
        Waits until the "_sent_interaction_response" attr is set to True before returning.
        """

        # if getattr(self, "_send_interaction_response_task", None):
        #     while not self._send_interaction_response_task.done():
        #         await asyncio.sleep(0.1)
        #     result = self._send_interaction_response_task.result()
        #     if 200 <= result.status < 300:
        #         pass
        #     else:
        #         fr = FakeResponse(status=500, reason="Failed to create webhook.")
        #         raise discord.HTTPException(fr, fr.reason)
        #     self._send_interaction_response_task = None

        pass

    async def trigger_typing(self, *args, **kwargs):
        await InteractionTyping(self).do_typing(sleep_forever=False)

    async def ack(self, *, ephemeral: bool = False):
        """
        Send an acknowledge payload to Discord for the interaction. The :func:`send` method does this
        automatically if you haven't called it yourself, but if you're doing a time-intensive operation
        (anything that takes longer than 5 seconds to send a response), you may want to send the ack
        yourself so that Discord doesn't discard your interaction.

        Args:
            ephemeral (bool, optional): Whether or not the ack is visible only to the user calling the
                command.
        """

        app_id, _, token = await self._get_channel()
        r = discord.http.Route('POST', '/interactions/{app_id}/{token}/callback', app_id=app_id, token=token)
        flags = discord.MessageFlags(ephemeral=ephemeral)
        await self._state.http.request(r, json={"type": self.ACK_RESPONSE_TYPE, "data": {"flags": flags.value}})
        self._sent_ack_response = True

    def typing(self, *args, **kwargs):
        return InteractionTyping(self)

    async def fetch_message(self, *args, **kwargs):
        raise Exception("This action is not available for this messagable type.")

    async def pins(self, *args, **kwargs):
        raise Exception("This action is not available for this messagable type.")

    def history(self, *args, **kwargs):
        raise Exception("This action is not available for this messagable type.")
