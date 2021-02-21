import logging
import typing

import asyncpg


class DatabaseConnection(object):
    """
    A helper class to wrap around an asyncpg.Connection object so as to make it a little easier to use.
    """

    config: dict = None
    pool: asyncpg.pool.Pool = None
    logger: logging.Logger = None
    __slots__ = ('conn', 'transaction', 'is_active',)

    def __init__(self, connection:asyncpg.Connection=None, transaction:asyncpg.transaction.Transaction=None):
        self.conn = connection
        self.transaction = transaction
        self.is_active = False

    @classmethod
    async def create_pool(cls, config:dict) -> None:
        """
        Creates the database pool and plonks it in DatabaseConnection.pool.

        Args:
            config (dict): The configuration for the dictionary, passed directly to `asyncpg.create_pool` as kwargs.
        """

        cls.config = config.copy()
        modified_config = config.copy()
        if modified_config.pop('enabled') is False:
            cls.logger.critical("Database create pool method is being run when the database is disabled")
            exit(1)
        cls.pool = await asyncpg.create_pool(**modified_config)

    @classmethod
    async def get_connection(cls) -> 'DatabaseConnection':
        """
        Acquires a connection to the database from the pool.

        Returns:
            DatabaseConnection: The connection that was aquired from the pool.
        """

        conn = await cls.pool.acquire()
        v = cls(conn)
        v.is_active = True
        return v

    async def disconnect(self) -> None:
        """
        Releases a connection from the pool back to the mix.
        """

        await self.pool.release(self.conn)
        self.conn = None
        self.is_active = False
        del self

    async def start_transaction(self):
        """
        Creates a database object for a transaction.
        """

        self.transaction = self.conn.transaction()
        await self.transaction.start()

    async def commit_transaction(self):
        """
        Commits the transaction wew lad.
        """

        await self.transaction.commit()
        self.transaction = None

    async def __aenter__(self):
        if self.is_active:
            raise Exception("Can't open a new database connection while currently connected.")
        v = await self.get_connection()
        self.conn = v.conn
        self.is_active = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    async def __call__(self, sql:str, *args) -> typing.Union[typing.List[dict], None]:
        """
        Runs a line of SQL and returns a list, if things are expected back,
        or None, if nothing of interest is happening.

        Args:
            sql (str): The SQL that you want to run.
            *args: The args that are passed to the SQL, in order.

        Returns:
            typing.Union[typing.List[dict], None]: The list of rows that were returned from the database.
        """

        # Check we don't want to describe the table
        if sql.casefold().startswith("describe table "):
            table_name = sql[len("describe table "):].strip("; ")
            return await self.__call__(
                """SELECT column_name, column_default, is_nullable, data_type, character_maximum_length
                FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name=$1""",
                table_name,
            )

        # Runs the SQL
        self.logger.debug(f"Running SQL: {sql} {args!s}")
        if 'select' in sql.casefold() or 'returning' in sql.casefold():
            x = await self.conn.fetch(sql, *args)
        else:
            await self.conn.execute(sql, *args)
            return

        # If it got something, return the dict, else None
        if x:
            return x
        if 'select' in sql.casefold() or 'returning' in sql.casefold():
            return []
        return None

    async def execute_many(self, sql:str, *args) -> None:
        """
        Runs an executemany query.

        Args:
            sql (str): The SQL that you want to run.
            *args: A list of tuples of arguments to sent to the database.
        """

        self.logger.debug(f"Running SQL: {sql} {args!s}")
        await self.conn.executemany(sql, args)
        return None

    async def copy_records_to_table(self, table_name:str, *, records:typing.List[typing.Any], columns:typing.Tuple[str]=None, timeout:float=None) -> str:
        """
        Copies a series of records to a given table.

        Args:
            table_name (str): The name of the table you want to copy to.
            records (typing.List[typing.Any]): The list of records you want to input to the database.
            columns (typing.Tuple[str], optional): The columns (in order) that you want to insert to.
            timeout (float, optional): The timeout for the copy command.

        Returns:
            str: The COPY status string
        """

        return await self.conn.copy_records_to_table(
            table_name=table_name, records=records,
            columns=columns, timeout=timeout
        )
