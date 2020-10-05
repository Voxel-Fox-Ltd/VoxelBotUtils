import argparse
import asyncio
import logging
import sys
import typing

from .cogs.utils.database import DatabaseConnection
from .cogs.utils.redis import RedisConnection


__all__ = (
    'get_default_program_arguments',
    'validate_sharding_information',
    'set_default_log_levels',
    'run_bot',
)


# Set up the loggers
def set_log_level(logger_to_change:logging.Logger, loglevel:str) -> None:
    """Set a logger to a default loglevel

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
def get_default_program_arguments() -> argparse.Namespace:
    """Get the default commandline args for the file

    Returns:
        argparse.Namespace: The arguments that were parsed
    """
    parser = argparse.ArgumentParser()
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
    args = parser.parse_args()
    args.shard_count = args.shardcount
    return args


# Set up loggers
logger = logging.getLogger('vflbotutils')


# Make sure the sharding info provided is correctish
# def validate_sharding_information(min_shard:int, max_shard:int, shard_count:int) -> typing.List[int]:
def validate_sharding_information(args:argparse.Namespace) -> typing.List[int]:
    """Validate the given shard information and make sure that what's passed in is accurate

    Args:
        min_shard (int): The minimum shard ID
        max_shard (int): The maximum shard ID
        shard_count (int): The shard count
    """

    if args.shard_count is None:
        args.shard_count = 1
        args.min = 0
        args.max = 0
    shard_ids = list(range(args.min, args.max + 1))
    if args.shard_count is None and (args.min or args.max):
        logger.critical("You set a min/max shard handler but no shard count")
        exit(1)
    if args.shard_count is not None and not (args.min is not None and args.max is not None):
        logger.critical("You set a shardcount but not min/max shards")
        exit(1)
    return shard_ids

# # Set up intents
# intents = discord.Intents(
#     guilds=True,  # guild/channel join/remove/update
#     members=True,  # member join/remove/update
#     bans=True,  # member ban/unban
#     emojis=True,  # emoji update
#     integrations=True,  # integrations update
#     webhooks=True,  # webhook update
#     invites=True,  # invite create/delete
#     voice_states=True,  # voice state update
#     presences=True,  # member/user update for games/activities
#     guild_messages=True,  # message create/update/delete
#     dm_messages=True,  # message create/update/delete
#     guild_reactions=True,  # reaction add/remove/clear
#     dm_reactions=True,  # reaction add/remove/clear
#     guild_typing=True,  # on typing
#     dm_typing=True,  # on typing
# )

# # Okay cool make the bot object
# bot = utils.Bot(
#     config_file=args.config_file,
#     activity=discord.Game(name="Reconnecting..."),
#     status=discord.Status.dnd,
#     case_insensitive=True,
#     shard_count=args.shardcount,
#     shard_ids=shard_ids,
#     shard_id=args.min,
#     max_messages=100,  # The lowest amount that we can actually cache
#     logger=logger.getChild('bot'),
#     allowed_mentions=discord.AllowedMentions(everyone=False),
#     intents=intents,
# )

def set_default_log_levels(bot, args):
    """Set the default levels for the logger"""

    logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s: %(message)s', stream=sys.stdout)

    # Set loglevel defaults
    set_log_level(logger, args.loglevel)
    set_log_level(bot.database.logger, args.loglevel)
    set_log_level(bot.redis.logger, args.loglevel)
    set_log_level('discord', args.loglevel)

    # Set loglevels by config
    set_log_level(logger, args.loglevel_bot)
    set_log_level(bot.database.logger, args.loglevel_database)
    set_log_level(bot.redis.logger, args.loglevel_redis)
    set_log_level('discord', args.loglevel_discord)


async def start_database_pool(bot):
    """Start the database pool connection"""

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
    else:
        logger.info("Database connection has been disabled")


async def start_redis_pool(bot):
    """Start the redis pool conneciton"""

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


def run_bot(bot):
    """Starts the bot, connects the database, runs the async loop forever"""

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
    loop.close()
