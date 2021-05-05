Interactions Howto
##########################################

Interactions such as slash commands and buttons are some sexy lil additions to Discord. As such, you'll probably want to use them. Fortunately, VoxelBotUtils makes this pretty easy. Aside from the howto, there's a :ref:`full API reference<interactions>` on the main API reference page.

Slash Commands
------------------------------------------

One of the inbuilt cogs in VBU allows you to automatically add all public commands (anything that's not a :func:`meta command<voxelbotutils.checks.meta_command>`, not an :func:`owner only command<discord.ext.commands.is_owner>`, and has its :attr:`add_slash_command<voxelbotutils.Command.add_slash_command>` attribute set to `True` - as is the default) as slash commands.

To [attempt to] add all of your commands as slash commands, run the :code:`!addslashcommands` command in your code, and the bot will attempt to convert all of your arguments and bulk-add the commands to Discord. If this conversion fails, you'll be given a straight traceback of the error instead of anything interpreted, so you can see exactly where the issue stems from.

Most issues stem from using :class:`discord.ext.commands.Greedy`, misordering your optional arguments (they must appear at the end), using even *slightly* complex group commands, and using converters that don't stem from a commonly converted types (though in this instance you can add a :code:`SLASH_COMMAND_ARG_TYPE` attribute to your converter for the bot to use).

Components
------------------------------------------

Components

Buttons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Buttons
