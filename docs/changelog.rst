Changelog
======================================

A human-readable list of changes between versions.

0.3.2
--------------------------------------

New Features
""""""""""""""""""""""""

Changed Features
""""""""""""""""""""""""

* If embeds are enabled, the footer of embeds will be changed to "currently live on Twitch" when the stream presence is set.

Bugs Fixed
""""""""""""""""""""""""

* Fix typo when creating website config.

0.3.1
--------------------------------------

New Features
""""""""""""""""""""""""

* Catch :ref:`discord.ext.commands.ConversionError` in the error handler.

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
