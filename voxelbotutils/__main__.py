import os

from .runner import get_default_program_arguments, validate_sharding_information, set_default_log_levels, run_bot
from . import Bot


def create_file(*path, content:str=None, throw_error:bool=False):
    for index, i in enumerate(path[:-1]):
        try:
            os.mkdir(f"./{os.sep.join(path[:index + 1])}")
        except FileExistsError as e:
            if throw_error:
                raise e


if __name__ == '__main__':

    # Wew let's see if we want to run a bot
    parser = get_default_program_arguments(include_config_file=False)
    parser.add_argument("bot_directory", nargs="?", default=".", help="The directory containing a config and a cogs folder for the bot to run")
    parser.add_argument("--create-config-file", action="store_true", help="The bot will ignore running the bot, and instead create a config file as config/config.toml", default=False)
    args = parser.parse_args()

    # Let's see if we copyin bois
    if args.create_config_file:
        from . import config
        create_file("config", "config.toml", content=config.config_file.lstrip(), throw_error=True)
        create_file("config", "config.example.toml", content=config.config_file.lstrip())
        create_file("config", "database.pgsql", content=config.database_file.lstrip())
        create_file("cogs", "ping_command.py", content=config.cog_example.lstrip())
        create_file("run.bat", content="py -m voxelbotutils .\n")
        create_file("run.sh", content="python3 -m voxelbotutils .\n")
        create_file(".gitignore", content="__pycache__/\n*.toml\n!*.example*\nconfig/config.toml\n")
        create_file("requirements.txt", content="voxelbotutils\n")
        exit(1)

    # And run file
    shard_ids = validate_sharding_information(args)
    bot = Bot(shard_count=args.shardcount, shard_ids=shard_ids)
    set_default_log_levels(bot, args)
    run_bot(bot)
