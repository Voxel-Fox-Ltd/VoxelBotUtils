import datetime
import typing

from discord.ext import commands
from discord.ext.commands.core import wrap_callback

from .custom_cog import Cog


class Command(commands.Command):
    """
    A custom command object for wrapping our commands with.
    """

    def __init__(self, *args, **kwargs):
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

    def get_remaining_cooldown(self, ctx:commands.Context, current:float=None) -> typing.Optional[float]:
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

    def _prepare_cooldowns(self, ctx:commands.Context):
        """
        Prepares all the cooldowns for the command to be called.
        """

        if self._buckets.valid:
            current = ctx.message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()
            bucket = self._buckets.get_bucket(ctx.message, current)
            try:
                bucket.predicate(ctx)
            except AttributeError:
                ctx.bot.logger.critical(f"Invalid cooldown set on command {ctx.invoked_with}")
                raise commands.CheckFailure("Invalid cooldown set for this command")
            retry_after = bucket.update_rate_limit(current)
            if retry_after:
                try:
                    error = bucket.error
                except AttributeError:
                    error = bucket.default_cooldown_error
                raise error(bucket, retry_after)

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
        super().__init__(*args, cooldown_after_parsing=kwargs.get('cooldown_after_parsing', True), **kwargs)
        self.ignore_checks_in_help = kwargs.get('ignore_checks_in_help', False)
        self.locally_handled_errors: list = kwargs.get('locally_handled_errors', None)

    async def can_run(self, ctx:commands.Context) -> bool:
        """
        The normal Command.can_run but it ignores cooldowns.

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
        Add the usual utils.Command to the mix.
        """

        if 'cls' not in kwargs:
            kwargs['cls'] = Command
        return super().command(*args, **kwargs)

    def group(self, *args, **kwargs):
        """
        Add the usual utils.Group to the mix.
        """

        if 'cls' not in kwargs:
            kwargs['cls'] = Group
        if 'case_insensitive' not in kwargs:
            kwargs['case_insensitive'] = True
        return super().group(*args, **kwargs)

    def subcommand_group(self, *args, **kwargs):
        """
        Add the usual utils.Group to the mix.
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
