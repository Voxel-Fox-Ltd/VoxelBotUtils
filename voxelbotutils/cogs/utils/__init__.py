import re as _re
from discord.ext import commands as _dpy_commands

from . import checks, converters, errors, menus, interactions  # noqa - Interactions is only here for backdating
from .checks import cooldown  # noqa
from .context_embed import Embed  # noqa
from .custom_bot import MinimalBot, Bot, ComponentMessage  # noqa
from .custom_cog import Cog  # noqa
from .custom_command import Command, Group, SubcommandGroup  # noqa
from .custom_context import Context, AbstractMentionable, PrintContext  # noqa
from .database import DatabaseConnection  # noqa
from .redis import RedisConnection, RedisChannelHandler, redis_channel_handler  # noqa
from .statsd import StatsdConnection  # noqa
from .time_value import TimeValue  # noqa
from .interactions import *  # noqa
from .paginator import Paginator  # noqa
from .interactions.components import *  # noqa
from .help_command import HelpCommand  # noqa
from .models import ComponentMessage, ComponentWebhookMessage  # noqa
from .time_formatter import TimeFormatter  # noqa

# And now things we want to override our Dpy things with
from .dpy_checks import *  # noqa


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


_html_minifier = _re.compile(r"\s{2,}|\n")


def minify_html(text: str) -> str:
    return _html_minifier.sub("", text)
