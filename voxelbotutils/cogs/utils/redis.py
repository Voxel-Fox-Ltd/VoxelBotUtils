import logging
import typing

import aioredis


class RedisConnection(object):
    """
    A wrapper for an `aioredis.Redis` object.
    """

    config: dict = None
    pool: aioredis.Redis = None
    logger: logging.Logger = None  # Set as a child of bot.logger

    def __init__(self, connection:aioredis.RedisConnection=None):
        self.conn = connection

    @classmethod
    async def create_pool(cls, config:dict) -> None:
        """
        Creates and connects the pool object.

        Args:
            config (dict): The config dictionary that should be passed directly to `aioredis.create_redis_pool` directly as kwargs.
        """

        cls.config = config.copy()
        modified_config = config.copy()
        if modified_config.pop('enabled', True) is False:
            raise NotImplementedError("The Redis connection has been disabled.")
        address = modified_config.pop('host'), modified_config.pop('port')
        cls.pool = await aioredis.create_redis_pool(address, **modified_config)

    async def __aenter__(self):
        self.conn = self.pool
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    @classmethod
    async def get_connection(cls):
        """
        Acquires a connection from the connection pool.
        """

        conn = cls.pool
        return cls(conn)

    async def disconnect(self) -> None:
        """
        Releases a connection back into the connection pool.
        """

        del self

    async def publish_json(self, channel:str, json:dict) -> None:
        """
        Publishes some JSON to a given redis channel.

        Args:
            channel (str): The name of the channel that you want to publish redis to.
            json (dict): The JSON that you want to publish.
        """

        self.logger.debug(f"Publishing JSON to channel {channel}: {json!s}")
        return await self.conn.publish_json(channel, json)

    async def publish(self, channel:str, message:str) -> None:
        """
        Publishes a message to a given redis channel.

        Args:
            channel (str): The name of the channel that you want to publish redis to.
            message (str): The message that you want to publish.
        """

        self.logger.debug(f"Publishing message to channel {channel}: {message}")
        return await self.conn.publish(channel, message)

    async def set(self, key:str, value:str) -> None:
        """
        Sets a key/value pair in the redis DB.

        Args:
            key (str): The key you want to set the value of
            value (str): The data you want to set the key to
        """

        self.logger.debug(f"Setting Redis key:value pair with {key}:{value}")
        return await self.conn.set(key, value)

    async def get(self, key:str) -> str:
        """
        Grabs a value from the Redis DB given a key.

        Args:
            key (str): The key that you want to get from the Redis database.

        Returns:
            str: The key from the database.
        """

        v = await self.conn.get(key)
        self.logger.debug(f"Getting Redis from key with {key}")
        if v:
            return v.decode()
        return v

    async def mget(self, *keys) -> typing.List[str]:
        """
        Grabs a value from the redis DB given a key.

        Args:
            key (str): The keys that you want to get from the database.

        Returns:
            typing.List[str]: The values from the Redis database associated with the given keys.
        """

        if not keys:
            return []
        v = await self.conn.mget(keys)
        self.logger.debug(f"Getting Redis from keys with {keys}")
        if v:
            return [i.decode() for i in v]
        return v
