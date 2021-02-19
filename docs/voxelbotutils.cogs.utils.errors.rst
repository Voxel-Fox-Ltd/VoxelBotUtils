Errors
================================

errors.ConfigNotSet
-------------------------------------------

.. autoclass:: voxelbotutils.errors.ConfigNotSet
    :members:

    This is a subclass of :ref:`dpy:DisabledCommand` raised exclusively by the :ref:`voxelbotutils.checks.is\_config\_set` check. For normal users, this should just say that the command is disabled.

errors.InvokedMetaCommand
-------------------------------------------

.. autoclass:: voxelbotutils.errors.InvokedMetaCommand
    :members:

    This is to be invoked by :ref:`voxelbotutils.checks.meta\_command`, and should just result in a silent failure.

errors.BotNotReady
-------------------------------------------

.. autoclass:: voxelbotutils.errors.BotNotReady

errors.IsNotVoter
-------------------------------------------

.. autoclass:: voxelbotutils.errors.IsNotVoter

errors.NotBotSupport
-------------------------------------------

.. autoclass:: voxelbotutils.errors.NotBotSupport

errors.IsSlashCommand
-------------------------------------------

.. autoclass:: voxelbotutils.errors.IsSlashCommand

errors.IsNotSlashCommand
-------------------------------------------

.. autoclass:: voxelbotutils.errors.IsNotSlashCommand

errors.MissingRequiredArgumentString
---------------------------------------------------------

.. autoclass:: voxelbotutils.errors.MissingRequiredArgumentString
    :members:

    This is a version of :ref:`discord.ext.commands.MissingRequiredArgument` that just takes a string as a parameter so you can manually raise it inside commands.

errors.InvalidTimeDuration
-------------------------------------------

.. autoclass:: voxelbotutils.errors.InvalidTimeDuration
    :members:

    A subclass of :ref:`discord.ext.commands.BadArgument` that's thrown when a user passes an invalid input to a :ref:`voxelbotutils.TimeValue` converter in a command.
