import logging
import re as regex

from discord.ext.commands import Cog as OriginalCog

from .custom_bot import CustomBot
from .database import DatabaseConnection


class CustomCog(OriginalCog):
    """
    A simple lil wrapper around the original discord Cog class that just adds a logger for me to use.

    Attributes:
        logger (logging.Logger): The logger that's assigned to the cog instance.
    """

    def __init__(self, bot:CustomBot, logger_name:str=None):
        self.bot = bot
        bot_logger = getattr(bot, "logger", logging.getLogger("bot"))
        if logger_name:
            self.logger = bot_logger.getChild(logger_name)
        else:
            self.logger = bot_logger.getChild(self.get_logger_name())

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
