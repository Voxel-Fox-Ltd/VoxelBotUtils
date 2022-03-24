Changelog
======================================

A human-readable list of changes between versions.

0.8.4
--------------------------------------

New Features
""""""""""""""""""""""""""""""""""""

* Add Dutch translations for the error text.
* Add :func:`translation` as a slightly easier-to-use ``gettext`` module wrapper.
* Add :attr:`BotConfig.bot_info.include_stats` for use with slash commands.

Changed Features
""""""""""""""""""""""""""""""""""""

* Add timer for letting shards identify with the sharder.
* Add ``info`` as an application command.
* Add ``application_command_meta`` to any auto-created menus.
* Add support for giving a custom ID to menu components.
* Ask for messages in the menu by use of modals.
* Force all settings menus to be done via slash command by default.

Bugs Fixed
""""""""""""""""""""""""""""""""""""

* Fix webhook logging for statsd.
* Add a :class:`ApplicationCommandMeta` to the settings command by default.
* Catch error in checking if a Twitch user is live.
* Catch error in sending errors for tasks (ironic, yes).
* Fix ``su`` command.
* Add timer for letting a shard identify in the sharder.

0.8.3
--------------------------------------

New Features
"""""""""""""""""""""""""

* Dispatch :func:`twitch_stream` when a user goes live on Twitch, if the config is set properly.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Change ``donate`` to ``info`` in ``is_upgrade_chat_subscriber`` error.
* Support single file in embeddify.
* Change defaults of ``None`` to ``MISSING`` in embeddify.
* Catch error in connecting to shard manager.
* Fix ``ev`` over redis.
* Fix icon asset for oauth models in web utils.

0.8.2
--------------------------------------

New Features
"""""""""""""""""""""""""

* Add ``guild_only`` to :func:`menus.Menu.create_cog`.

Changed Features
"""""""""""""""""""""""""

* Readd ``image_url`` kwarg to ``Embeddify.send``.
* Oauth and bot info now default to false.
* ``addslashcommands`` and ``ev`` now output to file if their content is too long.
* Send added slash commands as a file when the output is too long.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Add missing ``await``s to transaction object.
* Change ``missing_perms`` to ``missing_permissions``.
* Fix stdout in ``ev`` command not being changed to embed if over 2000 characters.
* Fix naive datetime objects in connect event.
* Fix ``owners_ignore_check_failures`` flag in config.
* Fix buttons not being disabled in paginator.
* Fix missing import for transactions.

0.8.0
--------------------------------------

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed versioning for Jinja2.
* Fixed ``get_display_name`` method for Jinja2 templating.
* Fix ``PrintContext``.

New Features
"""""""""""""""""""""""""

* Add ``--connect`` arg to the interactions webserver.
* Support multiple database types.
    * The database type will be set to SQLite by default.

0.7.3
--------------------------------------

Side Notes
"""""""""""""""""""""""""

* ``Command`` and ``Group`` are essentially now identical to Novus' implementation. As such there's no longer a need to decorate with ``@voxelbotutils.command()``. It hasn't been removed, but new command types (like :func:`discord.ext.context_command`) have not been added.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Embeddify method no longer duplicates content.
* Fixed bot avatar sends in webhooks, help, and embeddify.
* Add ``SlashContext`` to init.
* Add missing ``label`` kwarg to a menu component.

Changed Features
"""""""""""""""""""""""""""""""""""""""

* Explicitly add a :class:`discord.ext.commands.CommandNotFound` response for slash commands.

New Features
"""""""""""""""""""""""""""""""""""""""

* Interactions webserver.

0.7.2
--------------------------------------

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed component interaction in the paginator.

Changed Features
"""""""""""""""""""""""""""""""""""""""

* The ``[p]stats`` embed now shows version infos for Novus, VBU, and Python.
* Fix ephemeral kwarg always being defined.
* ``[p]channelhelp`` and ``[p]commands`` are no longer added as slash commands.

New Features
""""""""""""""""""""""

* New (undocumented) embeddify method.

0.7.1
--------------------------------------

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fix ``avatar.url`` being deprecated..
* Fix ``Webhook.AsyncWebhookAdapter`` being deprecated.
* Fix slash command logging.
* Readd ``addslashcommands`` command.
* Fix ``Bot.get_invite_link``.
* Remove references to ``embeddify``.

0.7.0
--------------------------------------

Discord.py has died. I will now be maintaining both VoxelBotUtils and a Discord.py fork, `Novus <https://github.com/Voxel-Fox-Ltd/Novus>`_. As such, lot of features have thus moved from VBU over to Novus. 

* ``ComponentMessage`` is now redundant.
* ``bot_has_permissions`` is now redundant.
* Slash commands have been merged into Novus.
* Interactions have been moved into Novus as ``discord.ui.*``. The models remain the same.
* All slash command checks (and their errors) have been removed as they will be added to Novus. They have not yet been replicated.
* All cooldown subclasses have been removed, as Novus supports a dynamic cooldown system thanks to Danny. Thanks Danny.
* ``argparse`` is no longer interpreted by commands as Danny implemented a flags system which is - quite frankly - better.
* ``SubcommandGroup`` and its decorator have been removed, as Novus interprets this dynamically.
* ``InteractionMessageable`` has been superceded by :class:`discord.Interaction`.
* ``vbu.PartialChannel`` has been removed. Novus replaces this as :func:`discord.Client.get_partial_messageable`.
* ``vbu.TimeFormatter`` has been removed. Novus replaces this as :func:`discord.utils.format_dt`.
* ``Context.is_interaction`` has been removed. Novus replaces this as :attr:`discord.abc.Messageable.supports_ephemeral`.


0.6.6
--------------------------------------

New Features
"""""""""""""""""""""""""""""""""""""""

* Support enums in slash commands.
* Add :func:`component_check` method.
* Add :func:`format`.
* Add button commands.
* :class:`voxelbotutils.Paginator` now supports lists of embeds.

Changed Features
"""""""""""""""""""""""""""""""""""""""

* Add :code:`bot` attribute to :class:`ComponentInteractionPayload`.
* The :code:`runsql` command will now always use :code:`repr` instead of :code:`str`, and will output only to a file.
* Support :class:`enum.Enum`s in slash commands.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed errors in slash commands not being sent through properly.

0.6.5
--------------------------------------

New Features
"""""""""""""""""""""""""""""""""""""""

* Add vbu version to the auto-generated requirements file.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed slash command command check.

0.6.4
--------------------------------------

New Features
"""""""""""""""""""""""""""""""""""""""

* Add :func:`defer` check.

Changed Features
"""""""""""""""""""""""""""""""""""""""

* :code:`cogs.utils` is now imported automatically in your ev command.
* Update webhook timestamps to use Discord time formatters.
* Add different filtering for slash command adds.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed disabled commands being added as slash commands.

0.6.3
--------------------------------------

Changed Features
"""""""""""""""""""""""""""""""""""""""

* Set the default permission for :func:`menus.Menu.create_cog` to :code:`manage_guild`.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed cooldowns not parsing correctly for slash commands.
* Fixed the :code:`info` command raising an error for missing permissions for embeds.

0.6.2
--------------------------------------

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed subclass instances not being converted to slash commands properly.
* Fix statsd logging for slash commands.

0.6.1
--------------------------------------

Changed Features
"""""""""""""""""""""""""""""""""""""""

* Add :code:`post_invoke` kwarg to :func:`menus.Menu.create_cog`.
* Change how converters work for components in :class:`menus.Converter`.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed error where embeddified messages would require an author.
* Fix type hinting for :func:`menus.Menu.create_cog`

0.6.0
--------------------------------------

Breaking changes this time involve the messages intent becoming priviliged in time. Everything in this is to try to make that transition easier.

New Features
"""""""""""""""""""""""""""""""""""""""

* A new :code:`info` command and :class:`config<BotConfig.bot_info>`
* :code:`vbu run-shell` as a new :ref:`command line argument<cmd_run_shell>`.
* :code:`vbu commands [add|remove]` as a new :ref:`command line argument<cmd_commands>`.
* A drop-in replacement check for :func:`discord.ext.commands.bot_has_permissions` and :func:`discord.ext.commands.bot_has_guild_permissions` in the form of :func:`bot_has_permissions` and :func:`bot_has_guild_permissions`. These perform the original checks for message commands, and are ignored for application commands.

Changed Features
"""""""""""""""""""""""""""""""""""""""

* Fixed :func:`ComponentInteractionPayload.update_message` not functioning the same as :func:`discord.Message.edit`.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fix error where the paginator says components are undefined.
* Fix slash command arguments not being stripped.
* Fix slash command conversion errors not being dispatched.

Removed Features
"""""""""""""""""""""""""""""""""""""""

* :code:`help_command` and :code:`command_data` have been removed from the config. :code:`help_command` will still be parsed, but is no longer present in the default config file. A help command is not necessary in the world of slash commands, so configuring it is not high on the agenda.

0.5.10
--------------------------------------

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed menus being created without default permissions.

0.5.9
--------------------------------------

New Features
"""""""""""""""""""""""""""""""""""""""

* Support for context commands.

Changed Features
"""""""""""""""""""""""""""""""""""""""

* Updated the list of converted colours.
* Changed how slash commands/subcommands were parsed.
* :attr:`Bot.session` now logs to statsd.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed error where you couldn't set wait kwarg on :code:`TextChannel`s.

0.5.8
--------------------------------------

New Features
"""""""""""""""""""""""""""""""""""""""

* Handle disconnects and reconnects better in the shard manager.
* Handle pings and keepalives in the shard manager.
* :code:`target_id` is now supported in the slash command handler.
* Add an :attr:`argparse<voxelbotutils.Command.argparse>` attribute to the command decorator. The :code:`!addslashcommands` command is now updated to use this.

Changed Features
"""""""""""""""""""""""""""""""""""""""

* :code:`exc_info` is now returned properly on a startup failure.
* The :code:`send` command is no longer embeddified.
* The list of colours has been updated for the :class:`voxelbotutils.converters.ColourConverter`.

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""

* Fixed error in outputting the recommended shard count.

0.5.7
--------------------------------------

Changed Features
"""""""""""""""""""""""""""""""""""""""""""""""""

* Removed native UpgradeChat utils, and instead move them to an external dependancy.
* Change the eval command to not include globals, and include the VBU data in a :code:`vbu` arg.
* Changed the shard manager to use sockets instead of redis.

0.5.6
--------------------------------------

Bugs Fixed
"""""""""""""""""""""""""""""""""""""""""""""""""

* Fix error in creating a redis connection.

0.5.5
--------------------------------------

New Features
"""""""""""""""""""""""""""""""""""""""""""""""""

* Added a shard manager using redis.

0.5.4
--------------------------------------

Changed Features
"""""""""""""""""""""""""""""""""""""""""""""""""

* Remove caching from UpgradeChat utils.

Bugs Fixed
""""""""""""""""""""""""""""""""""""""""""""""""""

* Fix logger being undefined in UpgradeChat utils.

0.5.3
--------------------------------------

New Features
"""""""""""""""""""""""""""""""""""""""""""""""""

* Add :class:`voxelbotutils.TimeFormatter`.

Changed Features
"""""""""""""""""""""""""""""""""""""""""""""""""

* The bot will now say its recommended shard count before trying to connect.
* The :func:`voxelbotutils.Bot.create_global_application_command`, :func:`voxelbotutils.Bot.create_guild_application_command`, :func:`voxelbotutils.Bot.bulk_create_global_application_commands`, and :func:`voxelbotutils.Bot.bulk_create_guild_application_command`s will now return instances of :class:`voxelbotutils.ApplicationCommand`.

Bugs Fixed
""""""""""""""""""""""""""""""""""""""""""""""""""

* Temporarily fixed an issue where the bot wouldn't start without installing web requirements.
* Fix the embed kwarg not being usable for some embeds.

0.5.2
--------------------------------------

New Features
"""""""""""""""""""""""""""""""""""""""""""""""""

* Allow a bot parameter in :func:`voxelbotutils.menus.Menu.create_cog`.

Changed Features
""""""""""""""""""""""""""""""""""""""""""""""""""

* Message objects returned by the library will now be instances of :class:`voxelbotutils.ComponentMessage` or :class:`voxelbotutils.ComponentWebhookMessage`.
* Handle parameters to slash commands better instead of leaving them to D.py to be converted.
* Change the format on vbu's loggers.

Bugs Fixed
""""""""""""""""""""""""""""""""""""""""""""""""""

* Fixed an issue where paginators wouldn't expire cleanly.

0.5.1
--------------------------------------

Changed Features
""""""""""""""""""""""""""""""""""""""""""""""""""

* Allow select menus to be disabled
* Don't add a "menu loading" message for paginators.

0.5.0
--------------------------------------

This update is mainly to deal with breaking changes for the settings menus.

Changed Features
""""""""""""""""""""""""

* The settings menus have been entirely, incompatibly, redone.

0.4.0
--------------------------------------

This update is mainly to deal with breaking changes for the web utilities.

New Features
""""""""""""""""""""""""

* Added the :class:`voxelbotutils.web.OauthGuild`, :class:`voxelbotutils.web.OauthUser`, and :class:`voxelbotutils.web.OauthMember` classes.
* The :class:`discord.Message` and :class:`discord.WebhookMessage` objects have been replaced with subclasses that include message components.
* Added :class:`voxelbotutils.SelectMenu` and related objects.
* Message objects now have :code:`enable_components` and :code:`disable_components` methods.
* :class:`voxelbotutils.InteractionMessageable` now has a :func:`respond<voxelbotutils.InteractionMessageable.respond>` method that allows you to give a type 4 response to an interaction.

Changed Features
""""""""""""""""""""""""

* Raise :class:`voxelbotutils.errors.NotBotSupport` if the support guild cannot be fetched.
* If no scopes are given for :func:`voxelbotutils.Bot.get_invite_link`, the :attr:`bot's config<BotConfig.oauth.scopes>` will be used.
* Messages have had :code:`wait_for_button_click` removed in favour of :func:`discord.Client.wait_for`.
* :class:`voxelbotutils.Paginator` now uses buttons instead of reactions.
* :class:`voxelbotutils.Button` instances will now allow a label to be empty if an emoji is set.
* Components will now give you a :class:`discord.PartialMessage` instance if the message was not included in the interaction payload.

Bugs Fixed
""""""""""""""""""""""""

* Fixed bug when checking for reactions in the settings menus.
* Fixed a bug in the stats command for Python versions 3.9+.
* Add a missing module in the custom command object.
* Fix bug where file content would not be read in the ev command.
* Fix AttributeError when getting user mentions in slash commands.

0.3.2
--------------------------------------

New Features
""""""""""""""""""""""""

* Added :class:`voxelbotutils.MinimalBot`.
* The bot's startup logger line now includes the recommended number of shards that you should launch with.
* Added the :func:`voxelbotutils.web.is_logged_in` method.
* Add :code:`version` command to the CLI args.

Changed Features
""""""""""""""""""""""""

* If embeds are enabled, the footer of embeds will be changed to "currently live on Twitch" when the stream presence is set.
* If no permissions are given for :func:`voxelbotutils.Bot.get_invite_link`, the :attr:`bot's config<BotConfig.oauth.permissions>` will be used.
* Add :code:`remove_reaction` param to the :func:`voxelbotutils.Paginator.start` method.
* Made all :class:`voxelbotutils.Button` parameters into kwargs, *apart from* name and custom ID, which are positional.
* Add :func:`voxelbotutils.ComponentHolder.add_component` and :func:`voxelbotutils.ComponentHolder.remove_component` methods.
* Add :func:`voxelbotutils.MessageComponents.boolean_buttons` :func:`voxelbotutils.MessageComponents.add_buttons_with_rows` methods.

Bugs Fixed
""""""""""""""""""""""""

* Fix typo when creating website config.
* Fix the sharding information for when no arguments are set.
* Fix access token refreshing in :class:`voxelbotutils.UpgradeChat`.
* Fix button clicks not working with ephemeral messages.

0.3.1
--------------------------------------

New Features
""""""""""""""""""""""""

* Catch :class:`discord.ext.commands.ConversionError` in the error handler.

Changed Features
""""""""""""""""""""""""

* Set error text to be ephemeral when using slash commands.
* Allow bots to be created without a prefix (see :attr:`BotConfig.default_prefix`).

Bugs Fixed
""""""""""""""""""""""""

* Fix command name in errors when using subcommands.
* Fix setting the presence when there are no shard IDs set.
* Fix casting for args in slash commands.
* Fix login URL redirect for websites.
* Fixed `removeslashcommands` command.


0.3.0
--------------------------------------

Initial changelog version.
