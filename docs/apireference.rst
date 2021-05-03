API Reference
================================

Utils
---------------------------------------

Embed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Embed

Bot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

DatabaseConnection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.DatabaseConnection
   :no-special-members:

Paginator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Paginator

RedisConnection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.RedisConnection
   :no-special-members:

StatsdConnection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.StatsdConnection
   :no-special-members:

TimeValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.TimeValue

UpgradeChat Utils
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

UpgradeChat
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.UpgradeChat

UpgradeChatOrder
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.UpgradeChatOrder
   :no-special-members:

UpgradeChatOrderItem
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.UpgradeChatOrderItem
   :no-special-members:

UpgradeChatProduct
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.UpgradeChatProduct
   :no-special-members:

UpgradeChatUser
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.UpgradeChatUser
   :no-special-members:

UpgradeChatPaymentProcessor
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.UpgradeChatPaymentProcessor
   :no-special-members:

UpgradeChatProductType
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.UpgradeChatProductType
   :no-special-members:

UpgradeChatItemType
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.UpgradeChatItemType
   :no-special-members:

UpgradeChatInterval
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.UpgradeChatInterval
   :no-special-members:

Interactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Due to the complexity of interactions (such as slash commands and buttons), they've been moved to :ref:`their own page<interactionsmodule>` for the API reference, as well as having :ref:`another page<interactions>` for a basic howto guide.

.. toctree::

   voxelbotutils.cogs.utils.interactions

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


Settings Menus
------------------------------------------------------------

SettingsMenu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.SettingsMenu
   :no-special-members:

SettingsMenuOption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.SettingsMenuOption

SettingsMenuIterable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.SettingsMenuIterable
   :no-members:

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

web.add_discord_arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.add_discord_arguments

web.get_avatar_url
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_avatar_url

web.requires_login
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.requires_login

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
