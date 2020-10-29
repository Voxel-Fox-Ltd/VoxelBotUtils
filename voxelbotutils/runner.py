import argparse
import asyncio
import logging
import sys
import typing

from .cogs.utils.database import DatabaseConnection
from .cogs.utils.redis import RedisConnection
from .cogs.utils.custom_bot import CustomBot as Bot


__all__ = (
    'get_default_program_arguments',
    'validate_sharding_information',
    'set_default_log_levels',
    'run_bot',
)


# Set up the loggers
def set_log_level(logger_to_change:logging.Logger, loglevel:str) -> None:
    """
    Set a logger to a default loglevel

    Args:
        logger_to_change (logging.Logger): The logger you want to change
        loglevel (str): Description

    Returns:
        None

    Raises:
        ValueError: An invalid loglevel was passed to the method
    """

    if loglevel is None:
        return
    if isinstance(logger_to_change, str):
        logger_to_change = logging.getLogger(logger_to_change)
    level = getattr(logging, loglevel.upper(), None)
    if level is None:
        raise ValueError(f"The log level {loglevel.upper()} wasn't found in the logging module")
    logger_to_change.setLevel(level)


# Parse arguments
def get_default_program_arguments(include_config_file:bool=True) -> argparse.ArgumentParser:
    """
    Get the default commandline args for the file

    Args:
        include_config_file (bool, optional): Whether or not to include the config file arugment

    Returns:
        argparse.ArgumentParser: The arguments that were parsed
    """
    parser = argparse.ArgumentParser()
    if include_config_file:
        parser.add_argument("config_file", help="The configuration for the bot")
    parser.add_argument(
        "--min", type=int, default=None,
        help="The minimum shard ID that this instance will run with (inclusive)"
    )
    parser.add_argument(
        "--max", type=int, default=None,
        help="The maximum shard ID that this instance will run with (inclusive)"
    )
    parser.add_argument(
        "--shardcount", type=int, default=None,
        help="The amount of shards that the bot should be using"
    )
    parser.add_argument(
        "--loglevel", default="INFO",
        help="Global logging level - probably most useful is INFO and DEBUG"
    )
    parser.add_argument(
        "--loglevel-bot", default=None,
        help="Logging level for the bot - probably most useful is INFO and DEBUG"
    )
    parser.add_argument(
        "--loglevel-discord", default=None,
        help="Logging level for discord - probably most useful is INFO and DEBUG"
    )
    parser.add_argument(
        "--loglevel-database", default=None,
        help="Logging level for database - probably most useful is INFO and DEBUG"
    )
    parser.add_argument(
        "--loglevel-redis", default=None,
        help="Logging level for redis - probably most useful is INFO and DEBUG"
    )
    parser.add_argument(
        "--loglevel-statsd", default=None,
        help="Logging level for statsd - probably most useful is INFO and DEBUG"
    )
    return parser


# Set up loggers
logger = logging.getLogger('vflbotutils')


# Make sure the sharding info provided is correctish
def validate_sharding_information(args:argparse.Namespace) -> typing.List[int]:
    """
    Validate the given shard information and make sure that what's passed in is accurate

    Args:
        args (argparse.Namespace): The parsed argparse namespace for the program

    Returns:
        typing.List[int]: A list of shard IDs to use with the bot
    """

    if args.shardcount is None:
        args.shardcount = 1
        args.min = 0
        args.max = 0
    else:
        if args.min is None and args.max is None:
            args.min = 0
            args.max = args.shardcount - 1
        elif type(args.min) == int and type(args.max) == int:
            pass
        else:
            logger.critical("You set a shardcount but not min/max shards")
            exit(1)
    shard_ids = list(range(args.min, args.max + 1))
    if args.shardcount is None and (args.min or args.max):
        logger.critical("You set a min/max shard handler but no shard count")
        exit(1)
    if args.shardcount is not None and not (args.min is not None and args.max is not None):
        logger.critical("You set a shardcount but not min/max shards")
        exit(1)
    return shard_ids


def set_default_log_levels(bot:Bot, args:argparse.Namespace) -> None:
    """
    Set the default levels for the logger

    Args:
        bot (Bot): The custom bot object containing the logger, database logger, and redis logger
        args (argparse.Namespace): The argparse namespace saying what levels to set each logger to
    """

    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')
    bot.logger = logger

    # Make our streams
    bot_logger = logging.StreamHandler(sys.stdout)
    database_logger = logging.StreamHandler(sys.stdout)
    redis_logger = logging.StreamHandler(sys.stdout)
    stats_logger = logging.StreamHandler(sys.stdout)
    discord_logger = logging.StreamHandler(sys.stdout)

    # Add our formatters
    bot_logger.setFormatter(formatter)
    database_logger.setFormatter(formatter)
    redis_logger.setFormatter(formatter)
    stats_logger.setFormatter(formatter)
    discord_logger.setFormatter(formatter)

    # Set all the loggers to debug
    set_log_level(bot.logger, 'DEBUG')
    set_log_level(bot.database.logger, 'DEBUG')
    set_log_level(bot.redis.logger, 'DEBUG')
    set_log_level(bot.stats.logger, 'DEBUG')
    set_log_level('discord', 'DEBUG')

    # Set loglevel defaults for the stream handlers
    set_log_level(bot_logger, args.loglevel)
    set_log_level(database_logger, args.loglevel)
    set_log_level(redis_logger, args.loglevel)
    set_log_level(stats_logger, args.loglevel)
    set_log_level(discord_logger, args.loglevel)

    # Set loglevels for the streams via the commandline args
    set_log_level(bot_logger, args.loglevel_bot)
    set_log_level(database_logger, args.loglevel_database)
    set_log_level(redis_logger, args.loglevel_redis)
    set_log_level(stats_logger, args.loglevel_statsd)
    set_log_level(discord_logger, args.loglevel_discord)

    # Add the stream handlers to the loggers
    bot.logger.addHandler(bot_logger)
    bot.database.logger.addHandler(database_logger)
    bot.redis.logger.addHandler(redis_logger)
    bot.stats.logger.addHandler(stats_logger)
    logging.getLogger('discord').addHandler(discord_logger)


async def create_initial_database(bot:Bot) -> None:
    """
    Create the initial database using the internal database.psql file
    """

    # Open the db file
    try:
        with open("./config/database.pgsql") as a:
            data = a.read()
    except Exception:
        return False

    # Get the statements
    create_table_statements = []
    current_line = ''
    for line in data.split('\n'):
        if line.lstrip().startswith('--'):
            continue
        current_line += line + '\n'
        if line.endswith(';') and not line.startswith(' '):
            create_table_statements.append(current_line.strip())
            current_line = ''

    # Let's do it baybeee
    async with bot.database() as db:
        for i in create_table_statements:
            if i and i.strip():
                await db(i.strip())

    # Sick we're done
    return True


async def start_database_pool(bot:Bot) -> None:
    """
    Start the database pool connection
    """

    # Connect the database pool
    if bot.config['database']['enabled']:
        logger.info("Creating database pool")
        try:
            await DatabaseConnection.create_pool(bot.config['database'])
        except KeyError:
            raise Exception("KeyError creating database pool - is there a 'database' object in the config?")
        except ConnectionRefusedError:
            raise Exception("ConnectionRefusedError creating database pool - did you set the right information in the config, and is the database running?")
        except Exception:
            raise Exception("Error creating database pool")
        logger.info("Created database pool successfully")
        logger.info("Creating initial database tables")
        await create_initial_database(bot)
    else:
        logger.info("Database connection has been disabled")


async def start_redis_pool(bot:Bot) -> None:
    """
    Start the redis pool conneciton
    """

    # Connect the redis pool
    if bot.config['redis']['enabled']:
        logger.info("Creating redis pool")
        try:
            await RedisConnection.create_pool(bot.config['redis'])
        except KeyError:
            raise KeyError("KeyError creating redis pool - is there a 'redis' object in the config?")
        except ConnectionRefusedError:
            raise ConnectionRefusedError("ConnectionRefusedError creating redis pool - did you set the right information in the config, and is the database running?")
        except Exception:
            raise Exception("Error creating redis pool")
        logger.info("Created redis pool successfully")
    else:
        logger.info("Redis connection has been disabled")


def run_bot(bot:Bot) -> None:
    """
    Starts the bot, connects the database, runs the async loop forever

    Args:
        bot (Bot): The bot you want to run
    """

    # Use right event loop
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

    # Grab the event loop
    loop = bot.loop

    # Connect the database pool
    db_connect_task = start_database_pool(bot)
    loop.run_until_complete(db_connect_task)

    # Connect the redis pool
    re_connect = start_redis_pool(bot)
    loop.run_until_complete(re_connect)

    # Load the bot's extensions
    logger.info('Loading extensions... ')
    bot.load_all_extensions()

    # Run the bot
    try:
        logger.info("Running bot")
        loop.run_until_complete(bot.start())
    except KeyboardInterrupt:
        logger.info("Logging out bot")
        loop.run_until_complete(bot.logout())

    # We're now done running the bot, time to clean up and close
    if bot.config['database']['enabled']:
        logger.info("Closing database pool")
        loop.run_until_complete(DatabaseConnection.pool.close())
    if bot.config['redis']['enabled']:
        logger.info("Closing redis pool")
        RedisConnection.pool.close()

    logger.info("Closing asyncio loop")
    loop.stop()
    loop.close()
