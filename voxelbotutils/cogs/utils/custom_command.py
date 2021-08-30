import asyncio
import datetime
import typing
import argparse
import enum

from discord.ext import commands
from discord.ext.commands.core import wrap_callback

from .custom_context import PrintContext
from .custom_cog import Cog


class Command(commands.Command):
    """
    A custom command class subclassing :class:`discord.ext.commands.Command` so that we can add
    some more attirbutes to it. Unlike normal Discord.py, the :attr:`cooldown_after_parsing` attribute
    is set to `True` by default. Can be used in a normal :code:`@commands.command`'s `cls` attribute, but easier
    is to just use this library's :code:`@command`;

    ::

        @voxelbotutils.command()
        async def example(self, ctx):
            ...

    Attributes:
        locally_handled_errors (typing.List[discord.ext.commands.CommandError]): A list of errors
            that are handled by the command's :func:`on_error` method before being passed onto
            the main bot's error handler.
        add_slash_command (bool): Whether or not this command should be added as a slash command.
        argument_descriptions (typing.List[str]): A list of descriptions for the command arguments to
            be used in slash commands.
        argparse (typing.Tuple[str, ..., typing.Dict[str, typing.Any]]): A list of args and kwargs
            to be expanded into argparse.

            For instance, if you had a ban command and wanted to specify a ban time with a :code:`-days` flag,
            you could set that up like so:

            ::

                @voxelbotutils.command(argparse=(
                    ("-days", "-d", {"type": int, "default": 0, "nargs": "?"}),
                ))
                async def ban(self, ctx, user: discord.Member, *, namespace: argparse.Namespace):
                    ban_time: int = namespace.days  # Conversion is handled automatically
                    ...

        context_command_type (voxelbotutils.ApplicationCommandType): The type of context command that your
            given command should be added as.
        context_command_name (str): The name of the context command that should be added.
    """

    def __init__(self, *args, **kwargs):
        """:meta private:"""

        super().__init__(*args, cooldown_after_parsing=kwargs.pop('cooldown_after_parsing', True), **kwargs)
        self.locally_handled_errors: tuple = kwargs.get('locally_handled_errors', None)

    async def _actual_conversion(self, ctx, converter, argument, param):
        if isinstance(converter, (enum.Enum, enum.IntEnum, enum.EnumMeta)):
            try:
                return converter[argument]
            except Exception:
                pass
        return await super()._actual_conversion(ctx, converter, argument, param)

    async def dispatch_error(self, ctx, error):
        """
        Like how we'd normally dispatch an error, but we deal with local lads.

        :meta private:
        """

        # They didn't set anything? Default behaviour then
        if self.locally_handled_errors is None:
            return await super().dispatch_error(ctx, error)

        ctx.command_failed = True

        # See if we want to ping the local error handler
        if isinstance(error, self.locally_handled_errors):

            # If there's no `on_error` attr then this'll fail, but if there IS no `on_error`, there shouldn't
            # be anything in `self.locally_handled_errors` and we want to raise an error anyway /shrug
            injected = wrap_callback(self.on_error)
            if self.cog:
                ret = await injected(self.cog, ctx, error)
            else:
                ret = await injected(ctx, error)

            # If we ping the local error handler and it returned FALSE then we ping the other error handlers;
            # if not then we return here
            if ret is False:
                pass
            else:
                return ret

        # Ping the cog error handler
        try:
            if self.cog is not None:
                local = Cog._get_overridden_method(self.cog.cog_command_error)
                if local is not None:
                    wrapped = wrap_callback(local)
                    await wrapped(ctx, error)

        # Ping the global error handler
        except Exception:
            ctx.bot.dispatch('command_error', ctx, error)


class Group(commands.Group):

    def __init__(self, *args, **kwargs):
        """:meta private:"""

        super().__init__(*args, cooldown_after_parsing=kwargs.pop('cooldown_after_parsing', True), **kwargs)
        self.locally_handled_errors: tuple = kwargs.get('locally_handled_errors', None)

    def group(self, *args, **kwargs):
        """
        Add the usual :class:`voxelbotutils.Group` to the mix.
        """

        kwargs.setdefault('cls', Group)
        kwargs.setdefault('case_insensitive', self.case_insensitive)
        return super().group(*args, **kwargs)

    async def dispatch_error(self, ctx, error):
        """
        Like how we'd normally dispatch an error, but we deal with local lads.

        :meta private:
        """

        # They didn't set anything? Default behaviour then
        if self.locally_handled_errors is None:
            return await super().dispatch_error(ctx, error)

        ctx.command_failed = True

        # See if we want to ping the local error handler
        if isinstance(error, self.locally_handled_errors):

            # If there's no `on_error` attr then this'll fail, but if there IS no `on_error`, there shouldn't
            # be anything in `self.locally_handled_errors` and we want to raise an error anyway /shrug
            injected = wrap_callback(self.on_error)
            if self.cog:
                ret = await injected(self.cog, ctx, error)
            else:
                ret = await injected(ctx, error)

            # If we ping the local error handler and it returned FALSE then we ping the other error handlers;
            # if not then we return here
            if ret is False:
                pass
            else:
                return ret

        # Ping the cog error handler
        try:
            if self.cog is not None:
                local = Cog._get_overridden_method(self.cog.cog_command_error)
                if local is not None:
                    wrapped = wrap_callback(local)
                    await wrapped(ctx, error)

        # Ping the global error handler
        except Exception:
            ctx.bot.dispatch('command_error', ctx, error)
