import asyncio
import collections

from discord.abc import Messageable


FakeResponse = collections.namedtuple("FakeResponse", ["status", "reason"])


class InteractionMessageable(Messageable):

    async def _wait_until_interaction_sent(self):
        """
        Waits until the "_sent_interaction_response" attr is set to True before returning.
        """

        if getattr(self, "_send_interaction_response_task", None):
            while not self._send_interaction_response_task.done():
                await asyncio.sleep(0.1)
            result = self._send_interaction_response_task.result()
            if 200 <= result.status < 300:
                pass
            else:
                fr = FakeResponse(status=500, reason="Failed to create webhook.")
                raise discord.HTTPException(fr, fr.reason)
            self._send_interaction_response_task = None

    async def _get_channel():
        raise NotImplementedError()

    async def trigger_typing():
        raise Exception("This action is not available for this messagable type.")

    def typing():
        raise Exception("This action is not available for this messagable type.")

    async def fetch_message():
        raise Exception("This action is not available for this messagable type.")

    async def pins():
        raise Exception("This action is not available for this messagable type.")

    def history():
        raise Exception("This action is not available for this messagable type.")
