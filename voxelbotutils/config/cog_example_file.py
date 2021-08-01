cog_example = r'''
import voxelbotutils as vbu


class PingCommand(vbu.Cog):

    @vbu.command()
    async def ping(self, ctx: vbu.Context):
        """
        A sexy lil ping command for the bot.
        """

        await ctx.send("Pong!")


def setup(bot: vbu.Bot):
    x = PingCommand(bot)
    bot.add_cog(x)
'''
