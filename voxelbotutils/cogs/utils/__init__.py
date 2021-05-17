import re as _re
from discord.ext import commands as _dpy_commands

from . import checks, converters, errors, interactions  # Interactions is only here for backdating
from .checks import cooldown
from .context_embed import Embed
from .custom_bot import MinimalBot, Bot
from .custom_cog import Cog
from .custom_command import Command, Group, SubcommandGroup
from .custom_context import Context
from .database import DatabaseConnection
from .redis import RedisConnection, RedisChannelHandler, redis_channel_handler
from .statsd import StatsdConnection
from .time_value import TimeValue
from .settings_menu import SettingsMenu, SettingsMenuOption, SettingsMenuIterable, SettingsMenuConverter
from .interactions import ApplicationCommand, ApplicationCommandOption, ApplicationCommandOptionChoice, ApplicationCommandOptionType
from .upgrade_chat import (
    UpgradeChat, UpgradeChatOrder, UpgradeChatUser, UpgradeChatOrderItem, UpgradeChatInterval, UpgradeChatProduct,
    UpgradeChatItemType, UpgradeChatPaymentProcessor, UpgradeChatProductType,
)
from .paginator import Paginator
from .interactions.components import *


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
