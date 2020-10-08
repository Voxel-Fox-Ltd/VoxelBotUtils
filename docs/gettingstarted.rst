Getting Started
===========================================

The simplest case usage of this library, as with many, would be to just use everything as default.

Config File
-------------------------------------

To get started, you'll need to make a config file. The library is nice enough to do this for you if you run the module via the commandline:

.. code-block:: bash

    python -m voxelbotutils --create-config-file

Doing this will make a few files and folders:

* `config/config.toml` - this is your bot's configuration file
* `config/config.example.toml` - this is a git-safe version of your config file; you can commit this as you please
* `config/database.pgsql` - this file should contain your database schema; it'll be pushed to your bot's database at every startup
* `run.bat` and `run.sh` - these are just shortcuts to running your bot; you may need to edit them depending on how you have Python installed to your system
* `.gitignore` - a default Gitignore file to ignore your config file
* `cogs/ping_command.py` - explained below

The only file that's _guarenteed_ to be created by this process is `config/config.toml` - the other files will silently fail if they already exist in your directory.

Here's what your directory should look like after running this command:

.. code-block

   Root
      |--- config
         |--- config.toml
         |--- config.example.toml
         |--- database.pgsql
      |--- cogs
         |--- ping_command.py
      run.bat
      run.sh
      .gitignore

Running the Bot
---------------------------------------

At this point you're able to run your bot - there's several built-in commands that are loaded when the bot starts. Fortunately, I've made that pretty easy for you if you don't want to modify any of the default settings. Simply run the bot via the module, where `.` is the directory containing the config and cogs folders:

.. code-block:: bash

   python -m voxelbotutils .

The information in the bot's `config/config.toml` file will be used to run it, as well as automatically loading any files found in the `cogs/` folder, should they not start with an underscore (eg the file `cogs/test.py` would be loaded, but `cogs/_test.py` would not).

If your database is enabled when you start your bot, the information found in the `config/database.pgsql` will be automatically run.

Making a Cog
--------------------------------------

Making cogs is pretty much the same as you would do normally in Discord.py - here's an example:

.. code-block:: python

   import voxelbotutils as utils

   class PingCommand(utils.Cog):

      @utils.command()
      async def ping(self, ctx:utils.Context):
         """A sexy lil ping command for the bot"""

         await ctx.send("Pong!")

   def setup(bot:utils.Bot):
      x = PingCommand(bot)
      bot.add_cog(x)

As you can see, almost everything is pretty much the same, but I'll note some key differences here.

The cog we have inherits from `voxelbotutils.Cog`. By doing this you can skip out on an `__init__` function, as one is included automatically for you, and it means that the cog has a `.logger` attribute, which you can use to send logging information to your console a la `self.logger.info("Ping commmand has been invoked")`

Our command is defined with `voxelbotutils.command()`. This is literally identical to `discord.ext.commands.command(cls=voxelbotutils.Command)`.
