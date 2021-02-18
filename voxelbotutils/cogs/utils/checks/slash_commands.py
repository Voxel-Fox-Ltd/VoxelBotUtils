from discord.ext import commands

from ..interactions import InteractionContext


class IsSlashCommand(commands.DisabledCommand):
    """
    Raised when a given command failes the is_not_slash_command check.
    """

    pass


class IsNotSlashCommand(commands.DisabledCommand):
    """
    Raised when a given command failes the is_slash_command check.
    """

    pass


def is_slash_command():
    async def predicate(ctx):
        v = isinstance(ctx, InteractionContext)
        if v:
            return True
        raise IsNotSlashCommand()
    return commands.check(predicate)


def is_not_slash_command():
    async def predicate(ctx):
        v = isinstance(ctx, InteractionContext)
        if not v:
            return True
        raise IsSlashCommand()
    return commands.check(predicate)
