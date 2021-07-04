from discord.abc import Messageable


class PartialChannel(Messageable):

    def __init__(self, *, id, state):
        self.id = id
        self._state = state

    async def _get_channel(self):
        return self.id
