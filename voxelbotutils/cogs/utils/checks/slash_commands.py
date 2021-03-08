from discord.ext import commands

from ..interactions import InteractionContext


class IsSlashCommand(commands.DisabledCommand):
    """Raised when a given command failes the :func:`voxelbotutils.checks.is_not_slash_command` check."""


class IsNotSlashCommand(commands.DisabledCommand):
    """Raised when a given command failes the :func:`voxelbotutils.checks.is_slash_command` check."""


def is_slash_command():
    """
    Checks that the command has been invoked from a slash command.

    Raises:
        IsNotSlashCommand: If the command was not run as a slash command.
    """

    async def predicate(ctx):
        v = isinstance(ctx, InteractionContext)
        if v:
            return True
        raise IsNotSlashCommand()
    return commands.check(predicate)


def is_not_slash_command():
    """
    Checks that the command has not been invoked from a slash command.

    Raises:
        IsSlashCommand: If the command was run as a slash command.
    """

    async def predicate(ctx):
        v = isinstance(ctx, InteractionContext)
        if not v:
            return True
        raise IsSlashCommand()
    return commands.check(predicate)
