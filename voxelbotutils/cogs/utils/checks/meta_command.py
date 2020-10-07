from discord.ext import commands


class InvokedMetaCommand(commands.CheckFailure):
    """
    Raised on any command decorated with `@voxelfoxutils.checks.meta_command()`.
    This stops users from running commands that we've made for internal use only.
    """


def meta_command():
    """
    Stops users from being able to run this command.
    Should be caught and then reinvoked OR have ctx.invoke_meta set to `True`.

    Example:

        .. code-block:: python

            @voxelbotutils.command()
            @voxelbotutils.checks.meta_command()
            async def notrunnable(self, ctx, *args):
                '''This command can't be run by normal users'''

            @voxelbotutils.command()
            async def runnable(self, ctx):
                '''But you can still run the command like this'''
                ctx.invoke_meta = True
                await ctx.invoke(ctx.bot.get_command('notrunnable'), 1, 2, 3)
    """

    def predicate(ctx):
        if getattr(ctx, 'invoke_meta', False):
            return True
        raise InvokedMetaCommand()
    return commands.check(predicate)
