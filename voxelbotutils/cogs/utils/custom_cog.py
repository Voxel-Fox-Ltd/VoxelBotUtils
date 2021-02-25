import typing
import logging
import re as regex

from discord.ext.commands import Cog as OriginalCog

from .custom_bot import Bot
from .database import DatabaseConnection
from .redis import RedisChannelHandler


class Cog(OriginalCog):
    """
    A slightly modified cog class to allow for cache_setup and for the logger instance.

    Attributes:
        bot (discord.ext.commands.Bot): The bot instance that will be added to the cog.
        logger (logging.Logger): The logger that's assigned to the cog instance.
        redis_channels (typing.Set[RedisChannelHandler]): The redis channels that this cog handles.
    """

    def __init__(self, bot:Bot, logger_name:str=None):
        self.bot = bot
        bot_logger = getattr(bot, "logger", logging.getLogger("bot"))
        if logger_name:
            self.logger = bot_logger.getChild(logger_name)
        else:
            self.logger = bot_logger.getChild(self.get_logger_name())

        self.redis_channels: typing.Set[RedisChannelHandler] = set()
        for attr in dir(self):
            item = getattr(self, attr)
            if isinstance(item, RedisChannelHandler):
                item.cog = self
                self.redis_channels.add(item)

    def unload(self):
        for i in self.redis_channels:
            self.bot.loop.run_until_complete(i.unsubscribe())

    def get_logger_name(self, *prefixes, sep:str='.') -> str:
        """
        Gets the name of the class with any given prefixes, with sep as a seperator.
        """

        return sep.join(['cog'] + list(prefixes) + [self.__cog_name__.replace(' ', '')])

    @property
    def qualified_name(self) -> str:
        """
        Gets the "human readable" name of the class.
        """

        return regex.sub(r"(?:[A-Z])(?:(?:[a-z0-9])+|[A-Z]+$|[A-Z]+(?=[A-Z]))?", "\\g<0> ", super().qualified_name.replace(' ', '')).strip()

    async def cache_setup(self, database:DatabaseConnection):
        """
        A method that gets run when the bot's startup method is run - intended for setting up cached information
        in the bot object that aren't in the guild_settings or user_settings tables
        """

        pass
