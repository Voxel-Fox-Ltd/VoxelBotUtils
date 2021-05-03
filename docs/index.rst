VoxelBotUtils
=========================================

VoxelBotUtils is a library built as an extension for Discord.py to speed up Discord bot development. It includes a whole slew of features that are commonly used in a lot of bots so you don't need to keep writing them every time. Listed below are the features you get automatically (based on your config file, most of the time) but also included in the library are a bunch of utility classes and functions for if you still want to run your own bot class rather than having VoxelBotUtils do that for you automatically via CMD.

* Bot Stats cog

   * github command - links to a repo as set in your config
   * invite command - gives an invite link for your bot
   * vote command - gives a vote link to your bot on Top.gg
   * stats command - shows some statistics for your bot

* Logging using Python's :code:`logging.Logger` classes
* Webhook sends on different events
* Built-in error handling for all of Discord.py's errors
* Bot stats posting via StatsD and DataDog
* A help command that doesn't look like trash
* :doc:`Interactions handling<interactions>`

   * Slash commands
   * Buttons

* Misc Commands cog

   * server - give a link to your server
   * donate - give a link to your donate page
   * website - give a link to your website
   * info - shows information for a bot
   * echo - the classic echo command

* Owner Only cog

   * redis - run a command on all instances of your bot via redis
   * source - show the source for a command
   * message - send a message to a user or channel
   * ev - run arbitrary Python code
   * reload - reload a cog
   * runsql - run arbitrary Postgres code
   * botuser - change aspects of your bot user
   * su - run a command as another user
   * shell - run arbitrary shell code

* Presence auto-updating based on Twitch streamers
* Inbuilt prefix command

.. toctree::
   :maxdepth: 4
   :caption: Contents:

Documentation Contents
-----------------------

.. toctree::
   :maxdepth: 1

   gettingstarted
   apireference
