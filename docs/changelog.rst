Changelog
======================================

A human-readable list of changes between versions.

0.4.0
--------------------------------------

This update is mainly to deal with breaking changes for the web utilities.

New Features
""""""""""""""""""""""""

* Added the :class:`voxelbotutils.web.OauthGuild`, :class:`voxelbotutils.web.OauthUser`, and :class:`voxelbotutils.web.OauthMember` classes.

Changed Features
""""""""""""""""""""""""

* Raise :class:`voxelbotutils.errors.NotBotSupport` if the support guild cannot be fetched.
* If no scopes are given for :func:`voxelbotutils.Bot.get_invite_link`, the :attr:`bot's config<BotConfig.oauth.scopes>` will be used.

Bugs Fixed
""""""""""""""""""""""""

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
