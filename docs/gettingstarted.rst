.. raw:: html

    <style>
        dt, dd {
            margin-bottom: 0 !important;
        }
   </style>

Overview
===========================================

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

Command Line
---------------------------------------

There's a few things you can do via CMD with the library. None of which I will tell you.

Getting Started With Bots
---------------------------------------

To get started you'll first want to make a config file. Fortunately, making one is pretty easy, and can be done via CMD.

.. code-block:: bash

   python -m voxelbotutils create-config bot

Doing this will make a few files and folders:

* :code:`config/config.toml` - this is your bot's configuration file
* :code:`config/config.example.toml` - this is a git-safe version of your configuration file; you can commit this as you please
* :code:`config/database.pgsql` - this file should contain your database schema; it'll be pushed to your bot's database at every startup
* :code:`run.bat`, :code:`run.sh`, and :code:`run.py` - these are just shortcuts to running your bot; you may need to edit them depending on how you have Python installed to your system
* :code:`.gitignore` - a default Gitignore file to ignore your configuration file
* :code:`cogs/ping_command.py` - a simple base class that you can copy/paste to build new classes

Running the Bot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Running the bot is also available via the package at a CMD level.

.. code-block:: bash

   python -m voxelbotutils run-bot .

The information in the bot's :code:`config/config.toml` file will be used to run it, as well as automatically loading any files found in the :code:`cogs/` folder, should they not start with an underscore (eg the file :code:`cogs/test.py` would be loaded, but :code:`cogs/_test.py` would not).

If your database is enabled when you start your bot, the information found in the :code:`config/database.pgsql` will be automatically run.

Migrating
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're reading this, you *probably* already have a bot that you want to get using with VoxelBotUtils. Fortunately, migrating is pretty easy. Most base Discord.py classes work by default without alteration, and as such you can just run your existing bot with a VBU config file, and that can be that.

If you really want to get things going, you can change all of your :class:`@commands.command()` lines to :class:`@voxelbotutils.command()`, and any :class:`class Whatever(commands.Cog)` to :class:`class Whatever(voxelbotutils.Cog)`, and that's pretty much all your basic requirements out of the way.

Getting Started With Websites
-------------------------------------

To get started, you'll need to make a configuration file that VBU can use. The library is nice enough to do this for you if you run the module via the commandline:

.. code-block:: bash

   python -m voxelbotutils create-config website

Doing this will make a few files and folders:

* `config/website.toml` - this is your bot's configuration file
* `config/website.example.toml` - this is a git-safe version of your configuration file; you can commit this as you please
* `config/database.pgsql` - this file should contain your database schema
* `run_website.bat` and `run_website.sh` - these are just shortcuts to running your bot; you may need to edit them depending on how you have Python installed to your system
* `.gitignore` - a default Gitignore file to ignore your configuration file
* `cogs/ping_command.py` - explained below

The only file that's *guarenteed* to be created by this process is `config/config.toml` - the other files will silently fail if they already exist in your directory.

Here's what your directory should look like after running this command:

.. code-block:: none

   Root
      |--- config
         |--- website.toml
         |--- website.example.toml
         |--- database.pgsql
      |--- website
         |--- static
            |--- .gitkeep
         |--- templates
            |--- .gitkeep
         |--- frontend.py
         |--- backend.py
      run_webste.bat
      run_webste.sh
      .gitignore
      requirements.txt

Running the Website
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can write your website routes in the `frontend.py` and `backend.py` files (as well as any other files you specify in your config) and run your website like so:

.. code-block:: bash

   python -m voxelbotutils run-website .
