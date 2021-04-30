import asyncio
import collections

import discord
from discord.abc import Messageable, Typing


FakeResponse = collections.namedtuple("FakeResponse", ["status", "reason"])


class InteractionTyping(Typing):

    async def do_typing(self):
        if not self.messageable._sent_ack_response and not self.messageable._sent_message_response:
            async with self.messageable._send_interaction_response_lock:
                self.messageable.ack()


class InteractionMessageable(Messageable):

    IS_INTERACTION = True
    CAN_SEND_EPHEMERAL = True
    ACK_IS_EDITABLE = True
    ACK_RESPONSE_TYPE = 5

    def __init__(self):
        Messageable.__init__(self)
        self._send_interaction_response_lock = asyncio.Lock()  # A lock so we don't try to respond initially twice
        self._send_interaction_response_task = None  # The task for sending an initial "waiting" response
        self._sent_ack_response = False
        self._sent_message_response = False

        """
        If we want to respond before sending a pending response, we can use type 4 - this responds intially with a message.
            After doing this we want to respond using webhooks rather than the interaction endpoint.
        While pending we can send a type 5 response - this means that the interaction gets an ack and goes into a pending state.
            After doing this the first time we want to send an initial response again, and followup messages go to the webhook
            response endpoint.
        Buttons have the luxury of a type 6 response - an ack response that doesn't tell the user we're waiting.
            Button responses can go immediately to the webhook response endpoint after this ack is received.
        """

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
            await self.trigger_typing()
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

    async def _get_channel(self, *args, **kwargs):
        raise NotImplementedError()

    async def trigger_typing(self, *args, **kwargs):
        await InteractionTyping(self).do_typing()

    async def ack(self):
        app_id, _, token = await self._get_channel()
        r = discord.http.Route('POST', '/interactions/{app_id}/{token}/callback', app_id=app_id, token=token)
        await self._state.http.request(r, json={"type": self.ACK_RESPONSE_TYPE})
        self._sent_ack_response = True

    def typing(self, *args, **kwargs):
        return InteractionTyping(self)

    async def fetch_message(self, *args, **kwargs):
        raise Exception("This action is not available for this messagable type.")

    async def pins(self, *args, **kwargs):
        raise Exception("This action is not available for this messagable type.")

    def history(self, *args, **kwargs):
        raise Exception("This action is not available for this messagable type.")
