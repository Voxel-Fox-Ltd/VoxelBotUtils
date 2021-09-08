from __future__ import annotations

import logging
import typing
import os

if typing.TYPE_CHECKING:
    from .types import (
        UserDatabaseConfig, DatabaseConfig, DriverWrapper,
        DriverPool, DriverConnection,
    )

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass


# Load our wrapper for our wrapper
Driver: typing.Type[DriverWrapper]
DATABASE_TYPE = os.getenv("VBU_DATABASE_TYPE", "postgres").lower()
if DATABASE_TYPE == "postgres":
    from .postgres import PostgresWrapper as Driver
elif DATABASE_TYPE == "mysql":
    from .mysql import MysqlWrapper as Driver
else:
    raise RuntimeError("Invalid database type passed")


class DatabaseTransaction(object):
    """
    A model for different driver transactions.
    """

    def __init__(self, driver: typing.Type[DriverWrapper], parent: DatabaseWrapper, *, commit_on_exit: bool = True):
        self._driver = driver
        self._parent = parent
        self._transaction = None
        self.is_active: bool = False
        self.commit_on_exit = commit_on_exit

    async def __aenter__(self) -> DatabaseTransaction:
        await self._driver.start_transaction(self)
        self.is_active = True
        return self

    async def __aexit__(self, *args):
        if not self.is_active:
            return
        if self.commit_on_exit and not any(args):
            await self.commit()
        else:
            await self._driver.rollback_transaction(self)

    async def __call__(self, *args, **kwargs):
        return self._parent(*args, **kwargs)

    async def execute_many(self, *args, **kwargs):
        return self._parent(*args, **kwargs)

    async def commit(self):
        await self._driver.commit_transaction(self)
        self.is_active = False


class DatabaseWrapper(object):
    """
    A wrapper around your preferred database driver.
    """

    __slots__ = ("conn", "is_active", "cursor",)

    config: typing.ClassVar[DatabaseConfig] = None  # type: ignore
    pool: typing.ClassVar[DriverPool] = None  # type: ignore
    logger: logging.Logger = logging.getLogger("vbu.database")
    enabled: typing.ClassVar[bool] = False

    def __init__(
            self, conn=None, *, cursor: DriverConnection = None):
        self.conn = conn
        self.cursor = cursor
        self.is_active = False

    @property
    def caller(self) -> DriverConnection:
        v = self.cursor or self.conn
        assert v
        return v

    @classmethod
    async def create_pool(cls, config: UserDatabaseConfig) -> None:
        """
        Create the database pool and store its instance in :attr:`pool`.

        Parameters
        ----------
        config: :class:`dict`
            The config that the pool should be created with.
        """

        # Grab the args that are valid
        config_args = ("host", "port", "database", "user", "password",)
        stripped_config: DatabaseConfig = {i: o for i, o in config.items() if i in config_args}  # type: ignore

        # See if we want to even enable the database
        if not config.get("enabled", True):
            raise RuntimeError("Database is not enabled in your config")

        # Start and store our pool
        created = await Driver.create_pool(stripped_config)
        assert created, "Failed to create database pool"
        cls.pool = created
        cls.enabled = True

    @classmethod
    async def get_connection(cls) -> DatabaseWrapper:
        """
        Acquires a connection to the database from the pool.

        Returns
        --------
        :class:`DatabaseWrapper`
            The connection that was aquired from the pool.
        """

        return await Driver.get_connection(cls)

    async def disconnect(self) -> None:
        """
        Releases a connection from the pool back to the mix.
        """

        await Driver.release_connection(self)

    async def __aenter__(self) -> DatabaseWrapper:
        new_connection = await self.get_connection()
        for i in self.__slots__:
            setattr(self, i, getattr(new_connection, i))
        return self

    async def __aexit__(self, *_) -> None:
        return await self.disconnect()

    def transaction(self, *args, **kwargs) -> DatabaseTransaction:
        return Driver.transaction(self, *args, **kwargs)

    async def __call__(self, sql: str, *args) -> typing.List[typing.Any]:
        """
        Runs a line of SQL and returns a list, if things are expected back, or None, if nothing of interest is happening.

        Args:
            sql (str): The SQL that you want to run.
            *args: The args that are passed to the SQL, in order.

        Returns:
            typing.Union[typing.List[dict], None]: The list of rows that were returned from the database.
        """

        assert self.conn, "No connection has been established"
        self.logger.debug(f"Running SQL: {sql} {args!s}")
        return await Driver.fetch(self, sql, *args)

    async def execute_many(self, sql: str, *args) -> None:
        raise NotImplementedError()

    async def copy_records_to_table(
            self, table_name: str, *, records: typing.List[typing.Any],
            columns: typing.Tuple[str] = None, timeout: float = None) -> str:
        raise NotImplementedError()
