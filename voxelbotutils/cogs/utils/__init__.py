import re as _re
from discord.ext import commands as _dpy_commands

from . import checks, converters, errors, menus
from .context_embed import Embed
from .custom_bot import MinimalBot, Bot
from .custom_cog import Cog
from .custom_command import Command, Group, SubcommandGroup
from .custom_context import Context, AbstractMentionable, PrintContext
from .database import DatabaseConnection
from .redis import RedisConnection, RedisChannelHandler, redis_channel_handler
from .statsd import StatsdConnection
from .time_value import TimeValue
from .interactions import *
from .paginator import Paginator
from .interactions.components import *
from .help_command import HelpCommand
from .time_formatter import TimeFormatter
from .string import Formatter

# And now things we want to override our Dpy things with
from .dpy_checks import *


def command(*args, **kwargs):
    return _dpy_commands.command(*args, cls=Command, **kwargs)


def group(*args, **kwargs):
    if 'case_insensitive' not in kwargs:
        kwargs['case_insensitive'] = True
    return _dpy_commands.group(*args, cls=Group, **kwargs)


_html_minifier = _re.compile(r"\s{2,}|\n")


def minify_html(text: str) -> str:
    return _html_minifier.sub("", text)


def defer(ephemeral: bool = False):
    """
    A defer check so that we can defer a response immediately when the command is run instead
    of after the converters have run.

    Args:
        ephemeral (bool, optional): Whether the defer should be ephemeral or not.
    """

    async def predicate(ctx: Context):
        await ctx.defer(ephemeral=ephemeral)
        return True
    return _dpy_commands.check(predicate)


defer_response = defer  # oops
_formatter = Formatter()
format = _formatter.format
db = DatabaseConnection
re = RedisConnection
