Getting Started
===========================================

The simplest case usage of this library, as with many, would be to just use everything as default.

Config File
-------------------------------------

To get started, you'll need to make a config file. The library is nice enough to do this for you if you run the module via the commandline:

.. code-block:: bash

    python -m voxelbotutils --create-config-file

Doing this will make a file `config/config.toml`. This file should be pretty self explanatory for your usage.

Making a Bot
--------------------------------------

Making the bot is the next part. I know this is very "step one, draw a circle; step two, draw the rest of the owl," but stay with me it's fine I promise.

The actual writing of the code for the bot is much the same as what you would do normally for cogs - make a folder called `cogs` in the same directory as your `config` file, so you have something looking like this:

.. code-block

   Root
      |--- config
         |--- config.toml
      |--- cogs

From there, you want to make a your cogs in the `cogs` directory. I'll give you an example one you can use:

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

Cogs in the cogs folder will be automatically loaded into the bot, unless their filename starts with an underscore (`_`). Of note here: the cog we have inherits from `voxelbotutils.Cog`, and our command is defined with `voxelbotutils.command`.

Running the Bot
---------------------------------------

Now we just gotta run it. Fortunately, I've made that pretty easy for you if you don't want to modify any of the default settings. Simply run the bot via the module, where `.` is the directory containing the config and cogs folders:

.. code-block:: bash

   python -m voxelbotutils .

The information in the bot's `config/config.toml` file will be used to run it. From there it should just stay online until you stop running the script. Nice.
