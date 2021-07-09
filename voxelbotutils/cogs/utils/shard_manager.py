import typing
import asyncio
import aiohttp
import enum
import logging

import aioredis

from .redis import RedisConnection


logger = logging.getLogger("vbu.sharder")


class ShardManagerOpCodes(enum.Enum):
    REQUEST_CONNECT = "REQUEST_CONNECT"  #: A bot asking to connect
    CONNECT_READY = "CONNECT_READY"  #: The manager saying that a given shard is allowed to connect
    CONNECT_COMPLETE = "CONNECT_COMPLETE"  #: A bot saying that a shard is done connecting
    PING = "PING"  #: A simple ack for the bot and sharder.
    PONG = "PONG"  #: A simple ack for the bot and sharder.


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
        self.priority_shards_waiting: typing.List[int] = []  #: A list of IDs of shards to connect ASAP.
        self.channel: 'aioredis.Channel' = None  #: The connected redis channel
        self.shard_connect_waiters = {}  #: A dictionary of events to see if a given shard has been pinged to connect.
        self.pong_received = asyncio.Event()  #: Whether or not the sharder has received a pong

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
            logger.debug(data)
            return data['session_start_limit']['max_concurrency']
        except Exception:
            logger.critical("Failed to get session start limit")
            raise

    async def get_redis_channel(self):
        if self.channel:
            return self.channel
        async with self.redis() as re:
            channel_list = await re.conn.subscribe("VBUShardManager")
        self.channel = channel_list[0]
        return self.channel

    async def run(self):
        """
        Connect and run the main event loop for the shard manager.
        """

        # Grab the channel "VBUShardManager"
        channel = await self.get_redis_channel()
        self.loop.create_task(self.shard_queue_handler())

        # Loop forever getting its messages
        logger.info('Waiting for messages on VBUShardManager')
        while (await channel.wait_message()):
            data: dict = await channel.get_json()
            logger.debug(f'Recieved message over VBUShardManager - {data}')

            # Make sure the data is valid
            if "op" not in data:
                logger.warning(f'Message is missing opcode or shard ID - {data}')
                continue

            # See which opcode we got
            opcode = data.get('op')
            if opcode == ShardManagerOpCodes.PING.value:
                await asyncio.sleep(0.5)  # Delay a bit
                async with self.redis() as re:
                    await re.publish("VBUShardManager", {"op": ShardManagerOpCodes.PONG.value})
            elif opcode == ShardManagerOpCodes.REQUEST_CONNECT.value:
                await self.shard_request(data.get('shard'), data.get('priority', False))
                continue
            elif opcode == ShardManagerOpCodes.CONNECT_COMPLETE.value:
                await self.shard_connected(data.get('shard'))
                continue
            elif opcode in [ShardManagerOpCodes.CONNECT_READY.value, ShardManagerOpCodes.PONG.value]:
                continue  # We send this - we don't need to read it

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
                if len(self.shards_connecting) < self.max_concurrency:
                    shard_id = None
                    if self.priority_shards_waiting:
                        shard_id = self.priority_shards_waiting.pop(0)
                    elif self.shards_waiting:
                        shard_id = self.shards_waiting.pop(0)
                    if shard_id is not None:
                        self.shards_connecting.append(shard_id)
                        self.loop.create_task(self.send_shard_connect(shard_id))
            await asyncio.sleep(0.1)

    async def shard_request(self, shard_id: int, priority: bool = False):
        """
        Add a shard to the waiting list for connections.

        Args:
            shard_id (int): The ID of the shard that's asking to connect.
            priority (bool): Whether or not this ID should be added to the priority waitlist.
        """

        async with self.lock:
            if shard_id in self.shards_waiting or shard_id in self.priority_shards_waiting:
                logger.info(f"Shard {shard_id} already in the connection waitlist")
                pass
            elif shard_id in self.shards_connecting:
                logger.info(f"Shard {shard_id} asked to connect again - resending connect payload")
                await asyncio.sleep(1)
                return await self.send_shard_connect(shard_id)
            else:
                if priority:
                    logger.info(f"Adding shard {shard_id} to the priority waitlist for connecting")
                    self.priority_shards_waiting.append(shard_id)
                else:
                    logger.info(f"Adding shard {shard_id} to the waitlist for connecting")
                    self.shards_waiting.append(shard_id)

    async def send_shard_connect(self, shard_id: int):
        """
        Handle telling a shard that it should connect.

        Args:
            shard_id (int): The ID of the shard that's asking to connect.
        """

        logger.info(f"Telling shard {shard_id} that it can connect now")
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

        logger.info(f"Shard {shard_id} connected - removing from the connecting shards list")
        async with self.lock:
            self.shards_connecting.remove(shard_id)

    async def channel_message_listener(self):
        """
        A task to be run while the shards for the bot are connecting.
        """

        async with self.redis() as re:
            logger.info("Sending ping opcode")
            await re.publish("VBUShardManager", {"op": ShardManagerOpCodes.PING.value})
        channel = await self.get_redis_channel()
        while (await channel.wait_message()):
            data: dict = await channel.get_json()
            opcode = data.get("op")
            if opcode == ShardManagerOpCodes.PONG.value:
                self.pong_received.set()
            elif opcode == ShardManagerOpCodes.CONNECT_READY.value:
                self.shard_connect_waiters.get(data.get("shard"), asyncio.Event()).set()

    async def ask_to_connect(self, shard_id: int, priority: bool = False):
        """
        A method for bots to use when connecting a shard. Waits until it recieves a message saying
        it's okay to connect before continuing.
        """

        await self.pong_received.wait()
        self.shard_connect_waiters[shard_id] = event = asyncio.Event()
        async with self.redis() as re:
            await re.publish("VBUShardManager", {
                "shard": shard_id,
                "op": ShardManagerOpCodes.REQUEST_CONNECT.value,
                "priority": priority,
            })
        await event.wait()

    async def done_connecting(self, shard_id: int):
        """
        A method for bots to use when connecting a shard. Waits until it recieves a message saying
        it's okay to connect before continuing.
        """

        async with self.redis() as re:
            await re.publish("VBUShardManager", {
                "shard": shard_id,
                "op": ShardManagerOpCodes.CONNECT_COMPLETE.value,
            })
