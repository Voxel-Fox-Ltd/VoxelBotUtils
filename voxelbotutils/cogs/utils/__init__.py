# flake8: noqa
from . import checks, converters, errors, interactions
from .checks import cooldown
from .context_embed import Embed
from .custom_bot import Bot
from .custom_cog import Cog
from .custom_command import Command, Group, SubcommandGroup
from .custom_context import Context
from .database import DatabaseConnection
from .redis import RedisConnection
from .statsd import StatsdConnection
from .time_value import TimeValue
from .settings_menu import SettingsMenu, SettingsMenuOption, SettingsMenuIterable, SettingsMenuIterableBase


from discord.ext import commands as _dpy_commands


def command(*args, **kwargs):
    return _dpy_commands.command(*args, cls=Command, **kwargs)


def group(*args, **kwargs):
    if 'case_insensitive' not in kwargs:
        kwargs['case_insensitive'] = True
    return _dpy_commands.group(*args, cls=Group, **kwargs)


def subcommand_group(*args, **kwargs):
    if 'case_insensitive' not in kwargs:
        kwargs['case_insensitive'] = True
    return _dpy_commands.group(*args, cls=SubcommandGroup, **kwargs)
