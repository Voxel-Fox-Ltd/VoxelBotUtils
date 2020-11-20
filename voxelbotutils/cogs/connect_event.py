from datetime import datetime as dt

import discord

from . import utils


class ConnectEvent(utils.Cog):

    async def send_webhook(self, text:str, username:str, logger:str) -> bool:
        """
        Send a webhook to the bot specified event webhook url.
        """

        if not self.bot.config.get("event_webhook_url"):
            return False
        await self.bot.event_webhook.send(text, username=username)
        self.logger.info(logger)
        return True

    @utils.Cog.listener()
    async def on_shard_connect(self, shard_id:int):
        """
        Ping a given webhook when the shard ID is connected.
        """

        await self.send_webhook(
            f"Shard connect event just pinged for shard ID `{shard_id}` - {dt.utcnow().strftime('%X.%f')}",
            f"{self.bot.user.name} - Shard Connect",
            f"Sent webhook for on_shard_connect event in shard `{shard_id}`",
        )

    @utils.Cog.listener()
    async def on_shard_ready(self, shard_id:int):
        """
        Ping a given webhook when the shard ID becomes ready.
        """

        await self.send_webhook(
            f"Shard ready event just pinged for shard ID `{shard_id}` - {dt.utcnow().strftime('%X.%f')}",
            f"{self.bot.user.name} - Shard Ready",
            f"Sent webhook for on_shard_ready event in shard `{shard_id}`",
        )

    @utils.Cog.listener()
    async def on_ready(self):
        """
        Ping a given webhook when the bot becomes ready.
        """

        await self.send_webhook(
            f"Bot ready event just pinged for instance with shards `{self.bot.shard_ids}` - {dt.utcnow().strftime('%X.%f')}",
            f"{self.bot.user.name} - Ready",
            "Sent webhook for on_ready event",
        )

    @utils.Cog.listener()
    async def on_shard_disconnect(self, shard_id:int):
        """
        Ping a given webhook when the shard ID is disconnected.
        """

        await self.send_webhook(
            f"Shard disconnect event just pinged for shard ID `{shard_id}` - {dt.utcnow().strftime('%X.%f')}",
            f"{self.bot.user.name} - Shard Disconnect",
            f"Sent webhook for on_shard_disconnect event in shard `{shard_id}`",
        )

    @utils.Cog.listener()
    async def on_disconnect(self):
        """
        Ping a given webhook when the bot is disconnected.
        """

        await self.send_webhook(
            f"Bot disconnect event just pinged for instance with shards `{self.bot.shard_ids}` - {dt.utcnow().strftime('%X.%f')}",
            f"{self.bot.user.name} - Disconnect",
            "Sent webhook for on_disconnect event",
        )


def setup(bot:utils.Bot):
    x = ConnectEvent(bot)
    bot.add_cog(x)
