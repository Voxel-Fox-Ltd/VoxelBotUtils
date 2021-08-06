API Reference
================================

Discord.py Changes
---------------------------------------

In order to make aspects of this library work, some aspects of the default Discord.py library have been modified. Though they present non-breaking behaviour, it's important to note them here.

* :code:`discord.abc.Messageable`'s send method and :code:`discord.Message`'s edit methods have been altered to have the :attr:`components` and :attr:`ephemeral` arguments. :attr:`components` refers to an instance of :class:`voxelbotutils.MessageComponents`, and :attr:`ephemeral` refers to whether or not the sent message should be ephemeral (which only works with interactions responses - slash commands and components).
* :code:`discord.ext.commands.bot_has_permissions` has been superseded by :code:`voxelbotutils.bot_has_permissions` as a drop-in replacement because the first is incompatible with slash commands.
* :code:`discord.ext.commands.bot_has_guild_permissions` has been superseded by :code:`voxelbotutils.bot_has_guild_permissions` as a drop-in replacement because the first is incompatible with slash commands.

Utils
---------------------------------------

Bot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.MinimalBot
   :exclude-members: close, invoke, login, start, __init__
   :no-inherited-members:

.. autoclass:: voxelbotutils.Bot
   :exclude-members: close, invoke, login, start
   :no-inherited-members:

Cog
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Cog
   :no-special-members:

Command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Command
   :no-special-members:

.. autoclass:: voxelbotutils.Group
   :no-special-members:

Context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Context
   :no-special-members:

AbstractMentionable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.AbstractMentionable

DatabaseConnection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.DatabaseConnection
   :no-special-members:

RedisConnection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.RedisConnection
   :no-special-members:

StatsdConnection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.StatsdConnection
   :no-special-members:

Embed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Embed
   :exclude-members: use_random_color

Paginator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Paginator

TimeValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.TimeValue

TimeFormatter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.TimeFormatter

ComponentMessage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.ComponentMessage
.. autoclass:: voxelbotutils.ComponentWebhookMessage

bot_has_permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.bot_has_permissions
.. autofunction:: voxelbotutils.bot_has_guild_permissions

Slash Commands
---------------------------------------------------

Slash commands also have :ref:`their own page<interactions howto>` for a basic integration guide.

ApplicationCommand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.ApplicationCommand

ApplicationCommandType
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.ApplicationCommandType

ApplicationCommandOption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.ApplicationCommandOption

ApplicationCommandOptionChoice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.ApplicationCommandOptionChoice

ApplicationCommandOptionType
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.ApplicationCommandOptionType

Components
---------------------------------------------------

Components also have :ref:`their own page<interactions howto>` for a basic integration guide.

InteractionMessageable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.InteractionMessageable
   :no-members:
   :no-special-members:
   :members: defer, respond

ComponentInteractionPayload
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.cogs.utils.interactions.components.ComponentInteractionPayload
   :no-members:
   :no-special-members:
   :members: defer, respond, defer_update, update_message

BaseComponent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.BaseComponent
   :exclude-members: to_dict, from_dict

   .. note::

      You will not need to make instances of this class - make instances of the child classes of this instead.

DisableableComponent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.DisableableComponent
   :exclude-members: to_dict, from_dict
   :show-inheritance:

   .. note::

      You will not need to make instances of this class - make instances of the child classes of this instead.

ComponentHolder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.ComponentHolder
   :exclude-members: to_dict, from_dict

   .. note::

      You will not need to make instances of this class - make instances of the child classes of this instead.

MessageComponents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.MessageComponents
   :exclude-members: to_dict, from_dict
   :show-inheritance:

ActionRow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.ActionRow
   :exclude-members: to_dict, from_dict
   :show-inheritance:

ButtonStyle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.ButtonStyle

Button
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Button
   :exclude-members: to_dict, from_dict
   :inherited-members:
   :show-inheritance:

SelectOption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.SelectOption
   :exclude-members: to_dict, from_dict
   :inherited-members:
   :show-inheritance:

SelectMenu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.SelectMenu
   :exclude-members: to_dict, from_dict
   :inherited-members:
   :show-inheritance:

Checks
-------------------------------------------------

checks.is_config_set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_config_set

checks.meta_command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.meta_command

checks.bot_is_ready
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.bot_is_ready

checks.is_bot_support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_bot_support

checks.is_voter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_voter

checks.is_upgrade_chat_subscriber
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_upgrade_chat_subscriber

checks.is_upgrade_chat_purchaser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_upgrade_chat_purchaser

checks.is_slash_command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_slash_command

checks.is_not_slash_command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_not_slash_command

checks.bot_in_guild
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.bot_in_guild

Cooldowns
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

cooldown.cooldown
"""""""""""""""""""""""""""""""""""

.. autofunction:: voxelbotutils.cooldown.cooldown

cooldown.no_raise_cooldown
"""""""""""""""""""""""""""""""""""

.. autofunction:: voxelbotutils.cooldown.no_raise_cooldown

cooldown.Cooldown
"""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.cooldown.Cooldown
   :exclude-members: __call__

cooldown.GroupedCooldownMapping
"""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.cooldown.GroupedCooldownMapping

cooldown.RoleBasedCooldown
"""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.cooldown.RoleBasedCooldown

Converters
----------------------------------------------------

converters.UserID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.UserID
   :no-special-members:
   :no-members:

converters.ChannelID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.ChannelID
   :no-special-members:
   :no-members:

converters.BooleanConverter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.BooleanConverter
   :no-special-members:
   :no-members:

converters.ColourConverter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.ColourConverter
   :no-special-members:
   :no-members:

converters.FilteredUser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.FilteredUser
   :no-special-members:
   :no-members:

converters.FilteredMember
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.FilteredMember
   :no-special-members:
   :no-members:


Menus
------------------------------------------------------------

Menus also have :ref:`their own page<menus howto>` for a basic integration guide.

menus.DataLocation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.DataLocation

menus.MenuCallbacks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.MenuCallbacks

menus.Check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.Check

menus.CheckFailureAction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.CheckFailureAction

menus.Converter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.Converter

menus.Option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.Option

menus.Menu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.Menu

menus.MenuIterable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.MenuIterable


Errors
-----------------------------------------------

errors.ConfigNotSet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.ConfigNotSet

errors.InvokedMetaCommand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.InvokedMetaCommand

errors.BotNotReady
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.BotNotReady

errors.IsNotVoter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.IsNotVoter

errors.NotBotSupport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.NotBotSupport
    :no-special-members:

errors.IsSlashCommand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.IsSlashCommand

errors.IsNotSlashCommand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.IsNotSlashCommand

errors.BotNotInGuild
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.BotNotInGuild

errors.MissingRequiredArgumentString
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.MissingRequiredArgumentString
    :no-special-members:

errors.InvalidTimeDuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.InvalidTimeDuration
    :no-special-members:

errors.IsNotUpgradeChatPurchaser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.IsNotUpgradeChatPurchaser
   :no-special-members:

errors.IsNotUpgradeChatSubscriber
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.IsNotUpgradeChatSubscriber
   :no-special-members:

Websites
---------------------------------------------------

web.OauthGuild
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.web.OauthGuild
   :no-special-members:

web.OauthUser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.web.OauthUser
   :no-special-members:

web.OauthMember
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.web.OauthMember
   :no-special-members:

web.add_discord_arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.add_discord_arguments

web.get_avatar_url
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_avatar_url

web.requires_login
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.requires_login

   .. seealso:: :func:`voxelbotutils.web.is_logged_in`

web.is_logged_in
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.is_logged_in

   .. seealso:: :func:`voxelbotutils.web.requires_login`

web.get_discord_login_url
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_discord_login_url

web.process_discord_login
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.process_discord_login

web.get_user_info_from_session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_user_info_from_session

web.get_access_token_from_session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_access_token_from_session

web.get_user_guilds_from_session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_user_guilds_from_session

web.add_user_to_guild_from_session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.add_user_to_guild_from_session
