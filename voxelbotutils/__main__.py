import argparse
import os

from .runner import run_bot, run_website


def create_file(*path, content:str=None, throw_error:bool=False):
    for index, i in enumerate(path[:-1]):
        try:
            os.mkdir(f"./{os.sep.join(path[:index + 1])}")
        except FileExistsError:
            pass
    try:
        with open(f"./{os.sep.join(path)}", "x") as a:
            a.write(content)
    except FileExistsError as e:
        if throw_error:
            raise e


# Parse arguments
def get_default_program_arguments() -> argparse.ArgumentParser:
    """
    Set up the program arguments for the module. These include the following (all are proceeded by "python -m voxelbotutils"):
    "run bot config.toml --min 0 --max 10 --shardcount 10"
    "run bot config/config.toml"
    "run website config.toml"
    "run website config/config.toml"
    "create-config bot"
    "create-config website"

    Returns:
        argparse.ArgumentParser: The arguments that were parsed
    """

    # LOGLEVEL_CHOICES = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    LOGLEVEL_CHOICES = ["debug", "info", "warning", "error", "critical"]
    # LOGLEVEL_CHOICES.extend([i.lower() for i in LOGLEVEL_CHOICES])

    # Set up our parsers and subparsers
    parser = argparse.ArgumentParser()
    runner_subparser = parser.add_subparsers(dest="subcommand")
    runner_subparser.required = True
    bot_subparser = runner_subparser.add_parser("run-bot")
    website_subparser = runner_subparser.add_parser("run-website")
    create_config_subparser = runner_subparser.add_parser("create-config")

    # Set up the bot arguments
    bot_subparser.add_argument("bot_directory", nargs="?", default=".", help="The directory containing a config and a cogs folder for the bot to run.")
    bot_subparser.add_argument("config_file", nargs="?", default="config/config.toml", help="The configuration for the bot.")
    bot_subparser.add_argument("--min", nargs="?", type=int, default=None, help="The minimum shard ID that this instance will run with (inclusive).")
    bot_subparser.add_argument("--max", nargs="?", type=int, default=None, help="The maximum shard ID that this instance will run with (inclusive).")
    bot_subparser.add_argument("--shardcount", nargs="?", type=int, default=None, help="The amount of shards that the bot should be using.")
    bot_subparser.add_argument("--loglevel", nargs="?", default="INFO", help="Global logging level - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    bot_subparser.add_argument("--loglevel-bot", nargs="?", default=None, help="Logging level for the bot - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    bot_subparser.add_argument("--loglevel-aiohttp", nargs="?", default=None, help="Logging level for aiohttp - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    bot_subparser.add_argument("--loglevel-discord", nargs="?", default=None, help="Logging level for discord - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    bot_subparser.add_argument("--loglevel-database", default=None, help="Logging level for database - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    bot_subparser.add_argument("--loglevel-redis", nargs="?", default=None, help="Logging level for redis - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    bot_subparser.add_argument("--loglevel-statsd", nargs="?", default=None, help="Logging level for statsd - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)

    # Set up the website arguments
    website_subparser.add_argument("website_directory", nargs="?", default=".", help="The directory containing a static and templates folder for the website to run.")
    website_subparser.add_argument("config_file", nargs="?", default="config/website.toml", help="The configuration for the website.")
    website_subparser.add_argument("--host", nargs="?", default="0.0.0.0", help="The host IP to run the website on.")
    website_subparser.add_argument("--port", nargs="?", type=int, default="8080", help="The port to run the website with.")
    website_subparser.add_argument("--debug", action="store_true", default=False, help="Whether or not to run the website in debug mode")
    website_subparser.add_argument("--loglevel", nargs="?", default="INFO", help="Global logging level - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    website_subparser.add_argument("--loglevel-web", nargs="?", default=None, help="Logging level for the website - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    website_subparser.add_argument("--loglevel-bot", nargs="?", default=None, help="Logging level for the bot - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    website_subparser.add_argument("--loglevel-aiohttp", nargs="?", default=None, help="Logging level for aiohttp - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    website_subparser.add_argument("--loglevel-discord", nargs="?", default=None, help="Logging level for discord - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    website_subparser.add_argument("--loglevel-database", nargs="?", default=None, help="Logging level for database - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    website_subparser.add_argument("--loglevel-redis", nargs="?", default=None, help="Logging level for redis - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    website_subparser.add_argument("--loglevel-statsd", nargs="?", default=None, help="Logging level for statsd - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)

    # See what we want to make a config file for
    create_config_subparser.add_argument("config_type", nargs=1, help="The type of config file that we want to create.", choices=["bot", "website", "all"])

    # Wew that's a lot of things
    return parser


if __name__ == '__main__':

    # Wew let's see if we want to run a bot
    parser = get_default_program_arguments()
    args = parser.parse_args()

    # Let's see if we copyin bois
    if args.subcommand == "create-config":
        config_type = args.config_type[0]
        from . import config
        if config_type in ["website", "all"]:
            website_frontend_file_content = (
                "from aiohttp.web import HTTPFound, Request, RouteTableDef\n"
                "from voxelbotutils import web as webutils\n"
                "import aiohttp_session\n"
                "import discord\n"
                "from aiohttp_jinja2 import template\n\n\n"
                "routes = RouteTableDef()\n"
            )
            website_backend_file_content = website_frontend_file_content + (
                "\n\n@routes.get('/login_processor')\n"
                "async def login_processor(request:Request):\n"
                '    """\n'
                '    Page the discord login redirects the user to when successfully logged in with Discord.\n'
                '    """\n\n'
                "    await webutils.process_discord_login(request)\n"
                "    session = await aiohttp_session.get_session(request)\n"
                "    return HTTPFound(location=session.pop('redirect_on_login', '/'))\n\n\n"
                "\n\n@routes.get('/logout')\n"
                "async def logout(request:Request):\n"
                '    """\n'
                "    Destroy the user's login session.\n"
                '    """\n\n'
                "    session = await aiohttp_session.get_session(request)\n"
                "    session.invalidate()\n"
                "    return HTTPFound(location='/')\n"
                "\n\n@routes.get('/login')\n"
                "async def login(request:Request):\n"
                '    """\n'
                "    Direct the user to the bot's Oauth login page.\n"
                '    """\n\n'
                '    return HTTPFound(location=webutils.get_discord_login_url(request, "/login_processor"))\n'
            ).replace("from aiohttp_jinja2 import template\n", "")
            create_file("config", "website.toml", content=config.web_config_file.lstrip(), throw_error=True)
            create_file("config", "website.example.toml", content=config.web_config_file.lstrip())
            create_file("config", "database.pgsql", content=config.database_file.lstrip())
            create_file("run_website.bat", content="py -m voxelbotutils run-website .\n")
            create_file("run_website.sh", content="python3 -m voxelbotutils run-website .\n")
            create_file(".gitignore", content="__pycache__/\nconfig/config.toml\nconfig/website.toml\n")
            create_file("requirements.txt", content="voxelbotutils[web]\n")
            create_file("website", "frontend.py", content=website_frontend_file_content)
            create_file("website", "backend.py", content=website_backend_file_content)
            create_file("website", "static", ".gitkeep", content="\n")
            create_file("website", "templates", ".gitkeep", content="\n")
            print("Created website config file.")
        if config_type in ["bot", "all"]:
            create_file("config", "config.toml", content=config.config_file.lstrip(), throw_error=True)
            create_file("config", "config.example.toml", content=config.config_file.lstrip())
            create_file("config", "database.pgsql", content=config.database_file.lstrip())
            create_file("cogs", "ping_command.py", content=config.cog_example.lstrip())
            create_file("run_bot.bat", content="py -m voxelbotutils run-bot .\n")
            create_file("run_bot.sh", content="python3 -m voxelbotutils run-bot .\n")
            create_file(".gitignore", content="__pycache__/\nconfig/config.toml\nconfig/website.toml\n")
            create_file("requirements.txt", content="voxelbotutils\n")
            print("Created bot config file.")
        exit(1)
    elif args.subcommand == "run-bot":
        run_bot(args)
    elif args.subcommand == "run-website":
        run_website(args)
