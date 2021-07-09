Changelog
======================================

A human-readable list of changes between versions.

0.5.5
--------------------------------------

New Features
"""""""""""""""""""""""""""""""""""""""""""""""""

* Added a shard manager.

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
