import random
import typing

import discord
from discord.ext import commands

from . import utils


class Help(utils.Cog):

    def __init__(self, bot: utils.Bot):
        super().__init__(bot)
        self._original_help_command = bot.help_command
        bot.help_command = utils.HelpCommand(dm_help=True)
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @utils.command(name="commands", hidden=True)
    async def _commands(self, ctx: utils.Context, *args):
        """
        An alias for help.
        """

        return await ctx.send_help(*args)

    @utils.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def channelhelp(self, ctx: utils.Context, *args):
        """
        An alias for help that outputs into the current channel.
        """

        return await ctx.send_help(*args)


def setup(bot: utils.Bot):
    x = Help(bot)
    bot.add_cog(x)
