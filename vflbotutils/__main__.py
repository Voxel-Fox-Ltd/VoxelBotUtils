import os

from .runner import get_default_program_arguments, get_package_folder, validate_sharding_information, set_default_log_levels, run_bot
from . import Bot


if __name__ == '__main__':
    # Wew let's see if we want to run a bot
    parser = get_default_program_arguments(include_config_file=False)
    parser.add_argument("bot_directory", nargs="?", default=".", help="The directory containing a config and a cogs folder for the bot to run")
    parser.add_argument("--create-config-file", action="store_true", help="The bot will ignore running the bot, and instead create a config file as config/config.toml", default=False)
    args = parser.parse_args()

    # Let's see if we copyin bois
    if args.create_config_file:
        try:
            os.mkdir("./config")
        except FileExistsError:
            pass
        with open(f"{get_package_folder()}/config/config.example.toml") as a:
            data = a.read()
        try:
            with open("./config/config.toml", "x") as a:
                a.write(data)
        except FileExistsError as e:
            raise FileExistsError("A config/config.toml file already exists in this directory") from e
        exit(1)

    # And run file
    shard_ids = validate_sharding_information(args)
    bot = Bot(shard_count=args.shardcount, shard_ids=shard_ids)
    set_default_log_levels(bot, args)
    run_bot(bot)
