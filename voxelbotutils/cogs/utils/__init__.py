# flake8: noqa
from . import checks, converters, errors
from .checks import cooldown
from .context_embed import ContextEmbed as Embed
from .custom_bot import CustomBot as Bot
from .custom_cog import CustomCog as Cog
from .custom_command import CustomCommand as Command
from .custom_command import CustomGroup as Group
from .custom_context import CustomContext as Context
from .database import DatabaseConnection
from .redis import RedisConnection
from .time_value import TimeValue
from .settings_menu import SettingsMenu, SettingsMenuOption, SettingsMenuIterable, SettingsMenuIterableBase


from discord.ext import commands as _dpy_commands


def command(*args, **kwargs):
    return _dpy_commands.command(*args, cls=Command, **kwargs)


def group(*args, **kwargs):
    return _dpy_commands.group(*args, cls=Group, **kwargs)
