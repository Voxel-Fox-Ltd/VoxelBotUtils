import discord
from discord.ext import commands

from . import utils


class MiscCommands(utils.Cog):

    @commands.command(aliases=['support', 'guild'], cls=utils.Command)
    @utils.checks.is_config_set('command_data', 'guild_invite')
    @commands.bot_has_permissions(send_messages=True)
    async def server(self, ctx:utils.Context):
        """
        Gives the invite to the support server.
        """

        await ctx.send(f"<{self.bot.config['command_data']['guild_invite']}>")

    @commands.command(aliases=['patreon'], cls=utils.Command)
    @utils.checks.is_config_set('command_data', 'donate_link')
    @commands.bot_has_permissions(send_messages=True)
    async def donate(self, ctx:utils.Context):
        """
        Gives you the bot's creator's donate link.
        """

        await ctx.send(f"<{self.bot.config['command_data']['donate_link']}>")

    @commands.command(cls=utils.Command)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(send_messages=True)
    @utils.checks.is_config_set('command_data', 'echo_command_enabled')
    async def echo(self, ctx:utils.Context, *, content:str):
        """
        Echos the given content into the channel.
        """

        await ctx.send(content, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))


def setup(bot:utils.Bot):
    x = MiscCommands(bot)
    bot.add_cog(x)
