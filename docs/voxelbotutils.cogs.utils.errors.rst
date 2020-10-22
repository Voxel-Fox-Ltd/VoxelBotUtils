Errors
================================

voxelbotutils.errors.ConfigNotSet
-------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.errors.ConfigNotSet
    :members:

    This is a subclass of `discord.ext.commands.DiabledCommand` raised exclusively by the `voxelbotutils.cogs.utils.checks.is_config_set.is_config_set` check. For normal users, this should just say that the command is disabled.

voxelbotutils.errors.InvokedMetaCommand
-------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.errors.InvokedMetaCommand
    :members:

    This is to be invoked by `voxelbotutils.cogs.utils.checks.meta_command.meta_command`, and should just result in a silent failure.

voxelbotutils.errors.MissingRequiredArgumentString
---------------------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.errors.MissingRequiredArgumentString
    :members:

    This is a version of `discord.ext.commands.MissingRequiredArgument` that just takes a string as a parameter so you can manually raise it inside commands.

voxelbotutils.errors.InvalidTimeDuration
-------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.errors.InvalidTimeDuration
    :members:

    A subclass of `discord.ext.commands.BadArgument` that's thrown when a user passes an invalid input to a `voxelbotutils.cogs.utils.time_value.TimeValue` converter in a command.
