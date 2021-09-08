import typing

import asyncpg

if typing.TYPE_CHECKING:
    import asyncpg.pool
    import asyncpg.transaction
    from .types import UserDatabaseConfig, DatabaseConfig, DriverWrapper, DriverPool
    from .model import DatabaseWrapper, DatabaseTransaction

    class PostgresDatabaseWrapper(DatabaseWrapper):
        config: UserDatabaseConfig
        pool: asyncpg.pool.Pool
        conn: typing.Optional[asyncpg.Connection]
        cursor: None
        caller: asyncpg.Connection

    class PostgresDatabaseTransaction(DatabaseTransaction):
        _parent: PostgresDatabaseWrapper
        _transaction: asyncpg.transaction.Transaction
        is_active: bool
        commit_on_exit: bool


class PostgresWrapper(DriverWrapper):

    @staticmethod
    async def create_pool(config: DatabaseConfig) -> asyncpg.pool.Pool:
        v = await asyncpg.create_pool(**config)
        assert v
        return v

    @staticmethod
    async def get_connection(dbw: typing.Type[PostgresDatabaseWrapper]) -> PostgresDatabaseWrapper:
        connection = await dbw.pool.acquire()
        v = dbw(
            conn=connection,
        )
        v.is_active = True
        return v

    @staticmethod
    async def release_connection(dbw: PostgresDatabaseWrapper) -> None:
        await dbw.pool.release(dbw.conn)
        dbw.conn = None
        dbw.is_active = False

    @classmethod
    async def start_transaction(cls, tra: PostgresDatabaseTransaction):
        assert tra._parent.conn
        transaction = tra._parent.conn.transaction()
        tra._transaction = transaction
        await transaction.start()

    @staticmethod
    async def commit_transaction(tra: PostgresDatabaseTransaction) -> None:
        await tra._transaction.commit()

    @staticmethod
    async def rollback_transaction(tra: PostgresDatabaseTransaction) -> None:
        await tra._transaction.rollback()

    @staticmethod
    async def fetch(dbw: PostgresDatabaseWrapper, sql: str, *args) -> typing.List[typing.Any]:
        x = None
        if 'select' in sql.casefold() or 'returning' in sql.casefold():
            x = await dbw.caller.fetch(sql, *args)
        else:
            await dbw.caller.execute(sql, *args)
        return x or list()
