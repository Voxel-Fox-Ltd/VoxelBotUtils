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

.. autoclass:: voxelbotutils.Group

Context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Context

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

checks.is\_config\_set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_config_set

checks.meta\_command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.meta_command

checks.bot\_is\_ready
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.bot_is_ready

checks.is\_bot\_support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_bot_support

checks.is\_voter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_voter

checks.is\_upgrade\_chat\_subscriber
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_upgrade_chat_subscriber

checks.is\_upgrade\_chat\_purchaser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_upgrade_chat_purchaser

Cooldowns
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

cooldown.cooldown
"""""""""""""""""""""""""""""""""""

.. autofunction:: voxelbotutils.cooldown.cooldown

cooldown.no\_raise\_cooldown
"""""""""""""""""""""""""""""""""""

.. autofunction:: voxelbotutils.cooldown.no_raise_cooldown

cooldown.Cooldown
"""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.cooldown.Cooldown

cooldown.GroupedCooldownMapping
"""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.cooldown.GroupedCooldownMapping

cooldown.CooldownWithChannelExemptions
""""""""""""""""""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.cooldown.CooldownWithChannelExemptions

cooldown.RoleBasedCooldown
"""""""""""""""""""""""""""""""""""

.. autoclass:: voxelbotutils.cooldown.RoleBasedCooldown

Converters
----------------------------------------------------

converters.UserID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.UserID

converters.ChannelID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.ChannelID

converters.EnumConverter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.EnumConverter

converters.BooleanConverter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.BooleanConverter

converters.ColourConverter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.ColourConverter

    It's just a normal colour converter that has the list of Wikipedia colour names as valid responses.

converters.FilteredUser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.FilteredUser

converters.FilteredMember
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.FilteredMember


Settings Menus
------------------------------------------------------------

Running one of these menus can be a *just a tad* unintuitive, so I'm putting an example on how to use it here.

.. code-block:: python

   # This creates a settings menu object
   menu = voxelbotutils.SettingsMenu()

   # This is just a shorthand function for getting a ping in the `bot.guild_settings` attr
   settings_mention = voxelbotutils.SettingsMenuOption.get_guild_settings_mention

   # Now we're gonna add options to our menu
   menu.add_option(
      voxelbotutils.SettingsMenuOption(
         ctx,

         # A function that returns a string to display
         display=lambda c: "Set setting (currently {0})".format(settings_mention(c, 'setting_id')),

         # A list of SettingsMenuConverter objects that should be used to convert the user inputs
         converter_args=[
            voxelbotutils.SettingsMenuConverter(
               prompt="What do you want to set the channel to?",
               asking_for="setting channel",
               converter=commands.TextChannelConverter,
            )
         ],

         # A callback that's used to add to the datbase and cache
         callback=voxelbotutils.SettingsMenuOption.get_set_settings_callback('guild_settings', 'guild_id', 'channel_id'),

         # Whether or not a null value is allowed (ie whether this value can be unset)
         allow_nullable=True,
      )
   )

   # Now we just run the menu
   await menu.start(ctx)

SettingsMenu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.SettingsMenu

SettingsMenuIterable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.SettingsMenuIterable

SettingsMenuOption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.SettingsMenuOption

Errors
-----------------------------------------------

errors.ConfigNotSet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.ConfigNotSet

    This is a subclass of :class:`discord.ext.commands.DisabledCommand` raised exclusively by the
    :func:`is\_config\_set<voxelbotutils.checks.is\_config\_set>` check. For normal users, this should just say
    that the command is disabled.

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
