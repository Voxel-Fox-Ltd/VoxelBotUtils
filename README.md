![GitHub stars badge](https://img.shields.io/github/stars/Voxel-Fox-Ltd/VoxelBotUtils)
![PyPi version info](https://img.shields.io/pypi/v/voxelbotutils.svg)
![PyPi Python versions](https://img.shields.io/pypi/pyversions/voxelbotutils.svg)
![Twitter badge](https://img.shields.io/twitter/url?url=https%3A%2F%2Fgithub.com%2FVoxel-Fox-Ltd%2FVoxelBotUtils)

# VoxelBotUtils

VoxelBotUtils (VBU) is an extension for Discord.py to speed up Discord bot development. It includes a whole slew of features that are commonly used in a lot of bots so you don't need to keep writing them every time. Many features are available to you by default:

* Built-in error handling for all of Discord.py's errors.
* Built-in database connector.
* Logging using Python's `logging.Logger` classes.
* Webhook sends on different events.
* Bot stats posting via StatsD and DataDog.
* A help command that doesn't look like trash.
* Owner-only commands.
* Presence auto-updating based on Twitch streamers.
* Website utilities.
* And more...

# Basic Usage

* Install VBU via pip - `pip install voxelbotutils`.
* Create your config file via CMD - `vbu create-config bot`.
* Update your auto-generated config file in `config/config.toml`.
* (Optional) Add/change any cogs you wish inside of the `cogs/` folder.
* Run your bot - `vbu run-bot`.

# Docs

Documentation for the package and its usage can be [found here](https://voxelbotutils.readthedocs.io/).

# Installing

The package is available via PyPi - `pip install voxelbotutils`. The tags on this repo can be used to keep up-to-date with different releases. The master branch is not guaranteed to be fully working, whereas PyPi releases are.
