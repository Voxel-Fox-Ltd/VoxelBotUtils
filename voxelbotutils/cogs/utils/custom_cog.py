import typing
import logging
import re

from discord.ext.commands import Cog as OriginalCog

from .custom_bot import Bot
from .database import DatabaseConnection
from .redis import RedisChannelHandler


class Cog(OriginalCog):
    """
    A slightly modified cog class to allow for the `cache_setup` method and for the class' `logger` instance.

    Attributes:
        bot (discord.ext.commands.Bot): The bot instance that will be added to the cog.
        logger (logging.Logger): The logger that's assigned to the cog instance.
    """

    def __init__(self, bot: Bot, logger_name: str = None):
        """:meta private:"""

        self.bot = bot
        bot_logger = getattr(bot, "logger", logging.getLogger("bot"))
        if logger_name:
            self.logger = bot_logger.getChild(logger_name)
        else:
            self.logger = bot_logger.getChild(self.get_logger_name())

        # Add the cog instance to redis channel handlers
        for attr in dir(self):
            try:
                item = getattr(self, attr)
            except AttributeError:
                continue
            if isinstance(item, RedisChannelHandler):
                item.cog = self

    def get_logger_name(self, *prefixes, sep: str = '.') -> str:
        """
        Gets the name of the class with any given prefixes, with sep as a seperator.
        """

        return sep.join(['cog'] + list(prefixes) + [self.__cog_name__.replace(' ', '')])

    @property
    def qualified_name(self) -> str:
        """
        Gets the "human readable" name of the class.
        """

        return re.sub(r"(?:[A-Z])(?:(?:[a-z0-9])+|[A-Z]+$|[A-Z]+(?=[A-Z]))?", "\\g<0> ", super().qualified_name.replace(' ', '')).strip()

    async def cache_setup(self, database: DatabaseConnection):
        """
        A method that gets run when the bot's startup method is run - intended for setting up cached information
        in the bot object that aren't in the :attr:`voxelbotutils.Bot.guild_settings` or :attr:`voxelbotutils.Bot.user_settings` tables.
        """

        pass
