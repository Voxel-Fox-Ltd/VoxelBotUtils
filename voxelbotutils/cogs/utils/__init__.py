import re as _re
from discord.ext import commands as _dpy_commands

from . import checks, converters, errors, menus
from .context_embed import Embed
from .custom_bot import MinimalBot, Bot
from .custom_cog import Cog
from .custom_command import Command, Group
from .custom_context import Context, AbstractMentionable, PrintContext, SlashContext
from .database import DatabaseWrapper, DatabaseTransaction
from .redis import RedisConnection, RedisChannelHandler, redis_channel_handler
from .statsd import StatsdConnection
from .time_value import TimeValue
from .paginator import Paginator
from .help_command import HelpCommand
from .string import Formatter
from .component_check import component_check
from .embeddify import Embeddify


def command(*args, **kwargs):
    return _dpy_commands.command(*args, cls=Command, **kwargs)


def group(*args, **kwargs):
    if 'case_insensitive' not in kwargs:
        kwargs['case_insensitive'] = True
    return _dpy_commands.group(*args, cls=Group, **kwargs)


_html_minifier = _re.compile(r"\s{2,}|\n")


def minify_html(text: str) -> str:
    return _html_minifier.sub("", text)


_formatter = Formatter()
format = _formatter.format
embeddify = Embeddify.send
DatabaseConnection = DatabaseWrapper
Database = DatabaseWrapper
Redis = RedisConnection
Stats = StatsdConnection
