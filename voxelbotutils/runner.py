import argparse
import asyncio
import logging
import sys
import typing
import os
import importlib

from .cogs.utils.database import DatabaseConnection
from .cogs.utils.redis import RedisConnection
from .cogs.utils.statsd import StatsdConnection
from .cogs.utils.custom_bot import Bot


class CascadingLogger(logging.getLoggerClass()):

    def setLevel(self, level):
        for i in self.handlers:
            if isinstance(i, logging.StreamHandler):
                if i.stream.name == "<stdout>":
                    i.setLevel(level)
                elif i.stream.name == "<stderr>":
                    i.setLevel(max([level, logging.WARNING]))
        super().setLevel(level)


logging.setLoggerClass(CascadingLogger)


# Set up the loggers
def set_log_level(
        logger_to_change: typing.Union[logging.Logger, str], log_level: str,
        minimum_level: int = None) -> None:
    """
    Set a logger to a default log level

    Args:
        logger_to_change (logging.Logger): The logger you want to change
        log_level (str): Description

    Returns:
        None

    Raises:
        ValueError: An invalid log_level was passed to the method
    """

    # Make sure we're setting it to something
    if log_level is None:
        return

    # Get the logger we want to change
    if isinstance(logger_to_change, str):
        logger_to_change = logging.getLogger(logger_to_change)

    # Get the log level
    try:
        level = getattr(logging, log_level.upper())
    except AttributeError:
        raise ValueError(f"The log level {log_level.upper()} wasn't found in the logging module")

    # Set the level
    if minimum_level is not None:
        logger_to_change.setLevel(max([level, minimum_level]))
    else:
        logger_to_change.setLevel(level)


# Set up loggers
logger = logging.getLogger('vbu')


# Make sure the sharding info provided is correctish
def validate_sharding_information(args: argparse.Namespace) -> typing.Optional[typing.List[int]]:
    """
    Validate the given shard information and make sure that what's passed in is accurate

    Args:
        args (argparse.Namespace): The parsed argparse namespace for the program

    Returns:
        typing.List[int]: A list of shard IDs to use with the bot
    """

    # Set up some short vars for us to use
    set_min_and_max = args.min is not None and args.max is not None
    set_shardcount = args.shardcount is not None

    # If we haven't said anything, assume one shard
    if not set_shardcount and not set_min_and_max:
        args.shardcount = 1
        return [0]

    # If we haven't set a min or max but we HAVE set a shardcount,
    # then assume we're using all shards
    if set_shardcount and not set_min_and_max:
        args.min = 0
        args.max = args.shardcount - 1

    # If we gave a min and max but no shardcount, that's just invalid
    if set_min_and_max and not set_shardcount:
        logger.critical("You set a min/max shard amount but no shard count")
        exit(1)

    # Work out the shard IDs to launch with
    shard_ids = list(range(args.min, args.max + 1))
    return shard_ids


# To make our log levels work properly, we need to set up a new filter for our stream handlers
# We're going to send most things to stdout, but a fair few sent over to stderr
class LogFilter(logging.Filter):
    """
    Filters (lets through) all messages with level < LEVEL.
    """

    # Props to these folks who I stole all this from
    # https://stackoverflow.com/a/28743317/2224197
    # http://stackoverflow.com/a/24956305/408556

    def __init__(self, filter_level: int):
        self.filter_level = filter_level

    def filter(self, record):
        # "<" instead of "<=": since logger.setLevel is inclusive, this should
        # be exclusive
        return record.levelno < self.filter_level


def _set_default_log_level(logger_name, log_filter, formatter, loglevel):
    logger = logging.getLogger(logger_name) if isinstance(logger_name, str) else logger_name

    set_log_level(logger, 'DEBUG')

    stdout_logger = logging.StreamHandler(sys.stdout)
    stdout_logger.addFilter(log_filter)
    stdout_logger.setFormatter(formatter)
    set_log_level(stdout_logger, loglevel)
    logger.addHandler(stdout_logger)

    stderr_logger = logging.StreamHandler(sys.stderr)
    stderr_logger.setFormatter(formatter)
    set_log_level(stderr_logger, loglevel, logging.WARNING)
    logger.addHandler(stderr_logger)

    # logger.warning("Test warning message")
    # logger.info("Test info message")
    # logger.error("Test error message")
    # logger.critical("Test critical message")


def set_default_log_levels(bot: Bot, args: argparse.Namespace) -> None:
    """
    Set the default levels for the logger

    Args:
        bot (Bot): The custom bot object containing the logger, database logger, and redis logger
        args (argparse.Namespace): The argparse namespace saying what levels to set each logger to
    """

    # formatter = logging.Formatter('%(asctime)s [%(levelname)s][%(name)s] %(message)s')
    # formatter = logging.Formatter('{asctime} | {levelname: <8} | {module}:{funcName}:{lineno} - {message}', style='{')
    formatter = logging.Formatter('{asctime} | {levelname: <8} | {name}: {message}', style='{')
    bot.logger = logger

    log_filter = LogFilter(logging.WARNING)

    loggers = [
        bot.logger,
        bot.database.logger,
        bot.redis.logger,
        bot.stats.logger,
        'discord',
        'aiohttp',
        'aiohttp.access',
        'upgradechat',
    ]
    for i in loggers:
        _set_default_log_level(i, log_filter, formatter, args.loglevel)


async def create_initial_database(db) -> None:
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
    for i in create_table_statements:
        if i and i.strip():
            await db(i.strip())

    # Sick we're done
    return True


async def start_database_pool(config: dict) -> None:
    """
    Start the database pool connection
    """

    # Connect the database pool
    logger.info("Creating database pool")
    try:
        await DatabaseConnection.create_pool(config['database'])
    except KeyError:
        raise Exception("KeyError creating database pool - is there a 'database' object in the config?")
    except ConnectionRefusedError:
        raise Exception(
            "ConnectionRefusedError creating database pool - did you set the right "
            "information in the config, and is the database running?"
        )
    except Exception:
        raise Exception("Error creating database pool")
    logger.info("Created database pool successfully")
    logger.info("Creating initial database tables")
    async with DatabaseConnection() as db:
        await create_initial_database(db)


async def start_redis_pool(config:dict) -> None:
    """
    Start the redis pool conneciton
    """

    # Connect the redis pool
    logger.info("Creating redis pool")
    try:
        await RedisConnection.create_pool(config['redis'])
    except KeyError:
        raise KeyError("KeyError creating redis pool - is there a 'redis' object in the config?")
    except ConnectionRefusedError:
        raise ConnectionRefusedError(
            "ConnectionRefusedError creating redis pool - did you set the right "
            "information in the config, and is the database running?"
        )
    except Exception:
        raise Exception("Error creating redis pool")
    logger.info("Created redis pool successfully")


def run_bot(args: argparse.Namespace) -> None:
    """
    Starts the bot, connects the database, runs the async loop forever

    Args:
        args (argparse.Namespace): The arguments namespace that wants to be run
    """

    os.chdir(args.bot_directory)

    # Use right event loop
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

    # And run file
    shard_ids = validate_sharding_information(args)
    bot = Bot(shard_count=args.shardcount, shard_ids=shard_ids, config_file=args.config_file)
    loop = bot.loop
    set_default_log_levels(bot, args)

    # Connect the database pool
    if bot.config.get('database', {}).get('enabled', False):
        db_connect_task = start_database_pool(bot.config)
        loop.run_until_complete(db_connect_task)

    # Connect the redis pool
    if bot.config.get('redis', {}).get('enabled', False):
        re_connect = start_redis_pool(bot.config)
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
        loop.run_until_complete(bot.close())

    # We're now done running the bot, time to clean up and close
    if bot.config.get('database', {}).get('enabled', False):
        logger.info("Closing database pool")
        try:
            loop.run_until_complete(asyncio.wait_for(DatabaseConnection.pool.close(), timeout=30.0))
        except asyncio.TimeoutError:
            logger.error("Couldn't gracefully close the database connection pool within 30 seconds")
    if bot.config.get('redis', {}).get('enabled', False):
        logger.info("Closing redis pool")
        RedisConnection.pool.close()

    logger.info("Closing asyncio loop")
    loop.stop()
    loop.close()


def run_website(args: argparse.Namespace) -> None:
    """
    Starts the website, connects the database, logs in the specified bots, runs the async loop forever

    Args:
        args (argparse.Namespace): The arguments namespace that wants to be run
    """

    # Load our imports here so we don't need to require them all the time
    from aiohttp.web import Application, AppRunner, TCPSite
    from aiohttp_jinja2 import setup as jinja_setup
    from aiohttp_session import setup as session_setup, SimpleCookieStorage
    from aiohttp_session.cookie_storage import EncryptedCookieStorage as ECS
    from jinja2 import FileSystemLoader
    import toml
    import re
    import html
    from datetime import datetime as dt
    import markdown

    os.chdir(args.website_directory)

    # Use right event loop
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

    # Read config
    with open(args.config_file) as a:
        config = toml.load(a)

    # Create website object - don't start based on argv
    app = Application(loop=asyncio.get_event_loop(), debug=args.debug)
    app['static_root_url'] = '/static'
    for route in config['routes']:
        module = importlib.import_module(f"website.{route}", "temp")
        app.router.add_routes(module.routes)
    app.router.add_static('/static', os.getcwd() + '/website/static', append_version=True)

    # Add middlewares
    if args.debug:
        session_setup(app, SimpleCookieStorage(max_age=1_000_000))
    else:
        session_setup(app, ECS(os.urandom(32), max_age=1_000_000))
    jinja_env = jinja_setup(app, loader=FileSystemLoader(os.getcwd() + '/website/templates'))

    # Add our jinja env filters
    def regex_replace(string, find, replace):
        return re.sub(find, replace, string, re.IGNORECASE | re.MULTILINE)

    def escape_text(string):
        return html.escape(string)

    def timestamp(string):
        return dt.fromtimestamp(float(string))

    def int_to_hex(string):
        return format(hex(int(string))[2:], "0>6")

    def to_markdown(string):
        return markdown.markdown(string, extensions=['extra'])

    def display_mentions(string, users):
        def get_display_name(group):
            user = users.get(group.group('userid'))
            if not user:
                return 'unknown-user'
            return user.get('display_name') or user.get('username')
        return re.sub(
            '(?:<|(?:&lt;))@!?(?P<userid>\\d{16,23})(?:>|(?:&gt;))',
            lambda g: f'<span class="chatlog__mention">@{get_display_name(g)}</span>',
            string,
            string,
            re.IGNORECASE | re.MULTILINE,
        )

    def display_emojis(string):
        def get_html(group):
            return (
                f'<img class="discord_emoji" src="https://cdn.discordapp.com/emojis/{group.group("id")}'
                f'.{"gif" if group.group("animated") else "png"}" alt="Discord custom emoji: '
                f'{group.group("name")}" style="height: 1em; width: auto;">'
            )
        return re.sub(
            r"(?P<emoji>(?:<|&lt;)(?P<animated>a)?:(?P<name>\w+):(?P<id>\d+)(?:>|&gt;))",
            get_html,
            string,
            re.IGNORECASE | re.MULTILINE,
        )

    jinja_env.filters['regex_replace'] = regex_replace
    jinja_env.filters['escape_text'] = escape_text
    jinja_env.filters['timestamp'] = timestamp
    jinja_env.filters['int_to_hex'] = int_to_hex
    jinja_env.filters['markdown'] = to_markdown
    jinja_env.filters['display_mentions'] = display_mentions
    jinja_env.filters['display_emojis'] = display_emojis

    # Add our connections and their loggers
    app['database'] = DatabaseConnection
    DatabaseConnection.logger = logger.getChild("database")
    app['redis'] = RedisConnection
    RedisConnection.logger = logger.getChild("redis")
    app['logger'] = logger.getChild("route")
    StatsdConnection.logger = logger.getChild("statsd")
    app['stats'] = StatsdConnection

    # Add our config
    app['config'] = config

    loop = app.loop

    # Connect the database pool
    if app['config'].get('database', {}).get('enabled', False):
        db_connect_task = start_database_pool(app['config'])
        loop.run_until_complete(db_connect_task)

    # Connect the redis pool
    if app['config'].get('redis', {}).get('enabled', False):
        re_connect = start_redis_pool(app['config'])
        loop.run_until_complete(re_connect)

    # Add our bots
    app['bots'] = {}
    for index, (bot_name, bot_config_location) in enumerate(config.get('discord_bot_configs', dict()).items()):
        bot = Bot(f"./config/{bot_config_location}")
        app['bots'][bot_name] = bot
        if index == 0:
            set_default_log_levels(bot, args)
        try:
            loop.run_until_complete(bot.login())
            bot.load_all_extensions()
        except Exception as e:
            logger.error(f"Failed to start bot {bot_name}")
            logger.error(e)
            exit(1)

    # Start the HTTP server
    logger.info("Creating webserver...")
    application = AppRunner(app)
    loop.run_until_complete(application.setup())
    webserver = TCPSite(application, host=args.host, port=args.port)

    # Start the webserver
    loop.run_until_complete(webserver.start())
    logger.info(f"Server started - http://{args.host}:{args.port}/")

    # This is the forever loop
    try:
        logger.info("Running webserver")
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # We're now done running the bot, time to clean up and close
    loop.run_until_complete(application.cleanup())
    if config.get('database', {}).get('enabled', False):
        logger.info("Closing database pool")
        try:
            loop.run_until_complete(asyncio.wait_for(DatabaseConnection.pool.close(), timeout=30.0))
        except asyncio.TimeoutError:
            logger.error("Couldn't gracefully close the database connection pool within 30 seconds")
    if config.get('redis', {}).get('enabled', False):
        logger.info("Closing redis pool")
        RedisConnection.pool.close()

    logger.info("Closing asyncio loop")
    loop.stop()
    loop.close()
