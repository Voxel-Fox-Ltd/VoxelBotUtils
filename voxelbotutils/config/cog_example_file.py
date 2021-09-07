cog_example = r'''
from discord.ext import commands, vbu


class PingCommand(vbu.Cog):

    @commands.command()
    async def ping(self, ctx: vbu.Context):
        """
        A sexy lil ping command for the bot.
        """

        await ctx.send("Pong!")


def setup(bot: vbu.Bot):
    x = PingCommand(bot)
    bot.add_cog(x)
'''
