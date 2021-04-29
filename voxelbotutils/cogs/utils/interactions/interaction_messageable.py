from discord.abc import Messageable


class InteractionMessageable(Messageable):

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
