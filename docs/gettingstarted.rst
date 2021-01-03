Overview
===========================================

Because I have a hard time selling people on VoxelBotUtils, I'm gonna give you a list of basic features that are provided with VoxelBotUtils by default, listed as bullet points.

* A default help command that doesn't look bad
* A series of owner-only commands including
    * eval (run arbitrary Python code)
    * sh (run a bash command)
    * su (run command as another user)
    * runsql (run arbitrary SQL)
* Builtin PostgreSQL database connection
* Builtin Redis connection
* Automatic guild count posting to Top.gg and DiscordBotList.org
* DataDog stats posting

There's more than that but that should be enough to either sell you on it or have you decide it's worthless.

Getting Started
===========================================

Configuration File
-------------------------------------

To get started, you'll need to make a configuration file that VBU can use. The library is nice enough to do this for you if you run the module via the commandline:

.. code-block:: bash

    python -m voxelbotutils create-config-file bot

Doing this will make a few files and folders:

* `config/config.toml` - this is your bot's configuration file
* `config/config.example.toml` - this is a git-safe version of your configuration file; you can commit this as you please
* `config/database.pgsql` - this file should contain your database schema; it'll be pushed to your bot's database at every startup
* `run.bat` and `run.sh` - these are just shortcuts to running your bot; you may need to edit them depending on how you have Python installed to your system
* `.gitignore` - a default Gitignore file to ignore your configuration file
* `cogs/ping_command.py` - explained below

The only file that's _guarenteed_ to be created by this process is `config/config.toml` - the other files will silently fail if they already exist in your directory.

Here's what your directory should look like after running this command:

.. code-block:: none

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

    python -m voxelbotutils run-bot .

The information in the bot's `config/config.toml` file will be used to run it, as well as automatically loading any files found in the `cogs/` folder, should they not start with an underscore (eg the file `cogs/test.py` would be loaded, but `cogs/_test.py` would not).

If your database is enabled when you start your bot, the information found in the `config/database.pgsql` will be automatically run.

Basic Cog Example
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

More Advanced Bot Example
--------------------------------------

There's no easy way to segue into it, so let's just have another cog example with a few more things. I'll give the example and then talk through everything of note.

.. code-block:: python

    import discord
    import voxelbotutils as utils

    class AnimalImageCommands(utils.Cog):

        @utils.command()
        async def cat(self, ctx:utils.Context):
            """
            Gives you a cat image
            """

            # Send request to the random cat API
            async with self.bot.session.get("https://aws.random.cat/meow") as r:
                data = await r.json()

            # Format it into an embed
            with utils.Embed(use_random_colour=True) as embed:
                embed.set_image(data['file'])
            await ctx.send(embed=embed)

            # Dispatch the context to event "on_animal_command"
            self.bot.dispatch("animal_command", ctx)

        @utils.Cog.listener()
        async def on_animal_command(self, ctx:utils.Context):
            """
            Add the user to the database
            """

            async with self.bot.database() as db:
                row_input = await db(
                    """INSERT INTO animal_commands (user_id, animal, count) VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, animal) DO UPDATE SET count=animal_commands.count+excluded.count RETURNING *""",
                    ctx.author.id, ctx.command.name, 1
                )
            user_animal_information = row_input[0]  # Data returned from DB calls is a list of dicts, so this would be [{'user_id': ctx.author.id, ...}]
            self.logger.info(f"Set {ctx.author.id}'s {ctx.command.name} usage to {user_animal_information['count']}")

    def setup(bot:utils.Bot):
        x = AnimalImageCommands(bot)
        bot.add_cog(x)

It's a bit of a jump from the previous example, but it shows a lot more.

Firstly, there's the use of `bot.session`, which is an instance of `aiohttp.ClientSession` - you can use this to run web requests through your bot. It's used pretty similarly to the `requests` library, if you're familiar with that. If you're familiar with aiohttp already, then this is just a session that stays open for the entire duration of your bot being online.

Secondly, there's the use of the context embeds - `voxelbotutils.Embed`. It's almost the same as a normal Discord.py embed, but you can use it in a `with` block, which I think makes it look a little cleaner. Included in that is the `use_random_colours` attribute, which would set the colour of the embed to a random number.

Thirdly, there's the use of the database. You can see in the custom event that we can open a database connection pretty easily with `async with bot.database() as db`, and then just using that to run your raw SQL. This is pretty much the gist of how the database calls work.

Migrating
--------------------------------------

If you're reading this, you _probably_ already have a bot that you want to get using with VoxelBotUtils. Fortunately, migrating is pretty easy. Most base Discord.py classes work by default without alteration, and as such you can just run your existing bot with a VBU config file, and that can be that.

If you really want to get things going, you can change all of your `@commands.command()` lines to `@voxelbotutils.command()`, and any `class Whatever(commands.Cog)` to `class Whatever(voxelbotutils.Cog)`, and that's pretty much all your basic requirements out of the way.
