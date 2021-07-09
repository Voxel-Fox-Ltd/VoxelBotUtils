import typing
import asyncio
import aiohttp
import enum
import logging

import aioredis

from .redis import RedisConnection


logger = logging.getLogger("shardmanager")


class ShardManagerOpCodes(enum.Enum):
    REQUEST_CONNECT = "REQUEST_CONNECT"  #: A bot asking to connect
    CONNECT_READY = "CONNECT_READY"  #: The manager saying that a given shard is allowed to connect
    CONNECT_COMPLETE = "CONNECT_COMPLETE"  #: A bot saying that a shard is done connecting


class ShardManager(object):
    """
    A small shard manager which handles launching a maximum amount of shards simultaneously.
    """

    redis = RedisConnection

    def __init__(self, max_concurrency: int = 1):
        """
        Args:
            max_concurrency (int, optional): The maximum amount of shards allowed to be connecting simultaneously
        """

        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()
        self.max_concurrency: int = max_concurrency  #: The maximum number of shards that can connect concurrently.
        self.shards_connecting: typing.List[int] = []  #: The IDs of the shards that are currently connecting.
        self.shards_waiting: typing.List[int] = []  #: The IDs of the shards that are waiting to connect.
        self.channel: 'aioredis.Channel' = None  #: The connected redis channel

    @staticmethod
    async def get_max_concurrency(token: str) -> int:
        """
        Ask Discord for the max concurrency of a bot given its token.

        Args:
            token (string): The token of the bot to request the maximum concurrency for

        Returns:
            int: The maximum concurrency for the given bot.
        """

        url = "https://discord.com/api/v9/gateway/bot"
        headers = {
            "Authorization": f"Bot {token}",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as r:
                    data = await r.json()
            return data['max_concurrency']
        except Exception:
            return 1  # We could gracefully fail here, but I don't care for it

    @classmethod
    async def get_redis_channel(cls):
        async with cls.redis() as re:
            channel_list = await re.conn.subscribe("VBUShardManager")
        return channel_list[0]

    async def run(self):
        """
        Connect and run the main event loop for the shard manager.
        """

        # Grab the channel "VBUShardManager"
        self.channel = await self.get_redis_channel()
        self.loop.create_task(self.shard_queue_handler())

        # Loop forever getting its messages
        while (await self.channel.wait_message()):
            data: dict = await self.channel.get_json()
            logger.debug(f'Recieved message over VBUShardManager - {data}')

            # Make sure the data is valid
            if any(("op" not in data, "shard" not in data)):
                logger.warning(f'Message is missing opcode or shard ID - {data}')
                continue

            # See which opcode we got
            if data.get('op') == ShardManagerOpCodes.REQUEST_CONNECT.value:
                await self.shard_request(data.get('shard'))
                continue
            elif data.get('op') == ShardManagerOpCodes.CONNECT_COMPLETE.value:
                await self.shard_connected(data.get('shard'))
                continue

            # Invalid opcode
            else:
                logger.warning(f'Message with invalid opcode received - {data}')
                continue

    async def shard_queue_handler(self):
        """
        Moves waiting shards to connecting if there's enough room available.
        """

        while True:
            async with self.lock:
                if self.shards_waiting and len(self.shards_connecting) < self.max_concurrency:
                    shard_id = self.shards_waiting.pop(0)
                    self.shards_connecting.append(shard_id)
                    self.loop.create_task(self.send_shard_connect(shard_id))
            await asyncio.sleep(0.1)

    async def shard_request(self, shard_id: int):
        """
        Add a shard to the waiting list for connections.

        Args:
            shard_id (int): The ID of the shard that's asking to connect.
        """

        async with self.lock:
            self.shards_waiting.append(shard_id)

    async def send_shard_connect(self, shard_id: int):
        """
        Handle telling a shard that it should connect.

        Args:
            shard_id (int): The ID of the shard that's asking to connect.
        """

        # Tell the shard it's able to connect
        async with self.redis() as re:
            await re.publish("VBUShardManager", {
                "shard": shard_id,
                "op": ShardManagerOpCodes.CONNECT_READY.value,
            })

    async def shard_connected(self, shard_id: int):
        """
        Handle receiving the signal on a shard having successfully connected.

        Args:
            shard_id (int): The ID of the shard that just connected.
        """

        async with self.lock:
            self.shards_connecting.remove(shard_id)

    @classmethod
    async def ask_to_connect(cls, shard_id: int):
        """
        A method for bots to use when connecting a shard. Waits until it recieves a message saying
        it's okay to connect before continuing.
        """

        channel = await cls.get_redis_channel()
        async with cls.redis() as re:
            await re.publish("VBUShardManager", {
                "shard": shard_id,
                "op": ShardManagerOpCodes.REQUEST_CONNECT.value,
            })
        while (await channel.wait_message()):
            data: dict = await channel.get_json()
            if data.get("op") == ShardManagerOpCodes.CONNECT_READY.value and data.get("shard") == shard_id:
                return

    @classmethod
    async def done_connecting(cls, shard_id: int):
        """
        A method for bots to use when connecting a shard. Waits until it recieves a message saying
        it's okay to connect before continuing.
        """

        async with cls.redis() as re:
            await re.publish("VBUShardManager", {
                "shard": shard_id,
                "op": ShardManagerOpCodes.CONNECT_COMPLETE.value,
            })
