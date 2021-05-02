import asyncio
import datetime
import typing

from discord.ext import commands
from discord.ext.commands.core import wrap_callback

from .custom_cog import Cog


class Command(commands.Command):
    """
    A custom command class subclassing :class:`discord.ext.commands.Command` so that we can add
    some more attirbutes to it. Unlike normal Discord.py, the :attr:`cooldown_after_parsing` attribute
    is set to `True` by default.

    Attributes:
        locally_handled_errors (typing.List[discord.ext.commands.CommandError]): A list of errors
            that are handled by the command's :func:`on_error` method before being passed onto
            the main bot's error handler.
        add_slash_command (bool): Whether or not this command should be added as a slash command.
    """

    def __init__(self, *args, **kwargs):
        """:meta private:"""

        super().__init__(*args, cooldown_after_parsing=kwargs.pop('cooldown_after_parsing', True), **kwargs)
        self.ignore_checks_in_help: bool = kwargs.get('ignore_checks_in_help', False)
        self.locally_handled_errors: list = kwargs.get('locally_handled_errors', None)
        self.add_slash_command: bool = kwargs.get('add_slash_command', True)

        # Fix cooldown to be our custom type
        cooldown = self._buckets._cooldown
        if cooldown is None:
            mapping = commands.CooldownMapping  # No mapping
        elif getattr(cooldown, 'mapping', None) is not None:
            mapping = cooldown.mapping  # There's a mapping in the instance
        elif getattr(cooldown, 'default_mapping_class') is not None:
            mapping = cooldown.default_mapping_class()  # Get the default mapping from the object
        else:
            raise ValueError("No mapping found for cooldown")
        self._buckets = mapping(cooldown)  # Wrap the cooldown in the mapping

    def get_remaining_cooldown(self, ctx: commands.Context, current: float = None) -> typing.Optional[float]:
        """
        Gets the remaining cooldown for a given command.

        Args:
            ctx (commands.Context): The context object for the command/author.
            current (float, optional): The current time.

        Returns:
            typing.Optional[float]: The remaining time on the user's cooldown or `None`.
        """

        bucket = self._buckets.get_bucket(ctx.message)
        return bucket.get_remaining_cooldown()

    async def _prepare_cooldowns(self, ctx: commands.Context):
        """
        Prepares all the cooldowns for the command to be called.
        """

        if self._buckets.valid:
            current = ctx.message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()
            bucket = self._buckets.get_bucket(ctx.message, current)
            try:
                coro = bucket.predicate(ctx)
                if asyncio.iscoroutine(coro) or asyncio.iscoroutinefunction(coro):
                    await coro
            except AttributeError:
                ctx.bot.logger.critical(f"Invalid cooldown set on command {ctx.invoked_with}")
                raise commands.CheckFailure("Invalid cooldown set for this command")
            retry_after = bucket.update_rate_limit(current)
            if retry_after:
                try:
                    error = bucket.error
                    if error is None:
                        raise AttributeError
                except AttributeError:
                    error = getattr(bucket, 'default_cooldown_error', commands.CommandOnCooldown)
                raise error(bucket, retry_after)

    async def prepare(self, ctx: commands.Context):
        """
        This is entirely stolen from the original method so I could make `prepare_cooldowns` an async
        method.

        https://github.com/Rapptz/discord.py/blob/a4d29e8cfdb91b5e120285b605e65be2c01f2c87/discord/ext/commands/core.py#L774-L795
        """

        ctx.command = self

        if not await self.can_run(ctx):
            raise CheckFailure('The check functions for command {0.qualified_name} failed.'.format(self))

        if self._max_concurrency is not None:
            await self._max_concurrency.acquire(ctx)

        try:
            if self.cooldown_after_parsing:
                await self._parse_arguments(ctx)
                await self._prepare_cooldowns(ctx)
            else:
                await self._prepare_cooldowns(ctx)
                await self._parse_arguments(ctx)

            await self.call_before_hooks(ctx)
        except Exception:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(ctx)
            raise

    async def dispatch_error(self, ctx, error):
        """
        Like how we'd normally dispatch an error, but we deal with local lads
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
        self.ignore_checks_in_help: bool = kwargs.get('ignore_checks_in_help', False)
        self.locally_handled_errors: list = kwargs.get('locally_handled_errors', None)
        self.add_slash_command: bool = kwargs.get('add_slash_command', True)

        # Fix cooldown to be our custom type
        cooldown = self._buckets._cooldown
        if cooldown is None:
            mapping = commands.CooldownMapping  # No mapping
        elif getattr(cooldown, 'mapping', None) is not None:
            mapping = cooldown.mapping  # There's a mapping in the instance
        elif getattr(cooldown, 'default_mapping_class') is not None:
            mapping = cooldown.default_mapping_class()  # Get the default mapping from the object
        else:
            raise ValueError("No mapping found for cooldown")
        self._buckets = mapping(cooldown)  # Wrap the cooldown in the mapping

    async def can_run(self, ctx: commands.Context) -> bool:
        """
        The normal :func:`discord.ext.Command.can_run` but it ignores cooldowns.

        Args:
            ctx (commands.Context): The command we want to chek if can be run.

        Returns:
            bool: Whether or not the command can be run.
        """

        if self.ignore_checks_in_help:
            return True
        try:
            return await super().can_run(ctx)
        except commands.CommandOnCooldown:
            return True

    def command(self, *args, **kwargs):
        """
        Add the usual :class:`voxelbotutils.Command` to the mix.
        """

        if 'cls' not in kwargs:
            kwargs['cls'] = Command
        return super().command(*args, **kwargs)

    def group(self, *args, **kwargs):
        """
        Add the usual :class:`voxelbotutils.Group` to the mix.
        """

        if 'cls' not in kwargs:
            kwargs['cls'] = Group
        if 'case_insensitive' not in kwargs:
            kwargs['case_insensitive'] = True
        return super().group(*args, **kwargs)

    def subcommand_group(self, *args, **kwargs):
        """
        Add the usual :class:`voxelbotutils.Group` to the mix.
        """

        if 'cls' not in kwargs:
            kwargs['cls'] = SubcommandGroup
        if 'case_insensitive' not in kwargs:
            kwargs['case_insensitive'] = True
        return super().group(*args, **kwargs)

    async def dispatch_error(self, ctx, error):
        """
        Like how we'd normally dispatch an error, but we deal with local lads
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


class SubcommandGroup(Group):
    """
    A subcommand group specifically made so that slash commands can be just a little sexier.
    """

    pass
