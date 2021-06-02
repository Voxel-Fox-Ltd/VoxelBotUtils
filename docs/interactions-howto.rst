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

Components are interactive additions to messages that you're able to send.

All interactions need to be placed into a :class:`MessageComponents` object, and that needs to be populated with :class:`ActionRow`s before finally allowing the components you *actually* want to send.

.. code-block:: python

   components = voxelbotutils.MessageComponents(
      voxelbotutils.ActionRow(
         voxelbotutils.Button("Finally")
      )
   )

Buttons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using buttons has been made pretty simple. First, you send your button to the user.

.. code-block:: python

   button1 = voxelbotutils.Button("Button 1")
   button2 = voxelbotutils.Button("Button 2")
   components = voxelbotutils.MessageComponents(
      voxelbotutils.ActionRow(button1, button2)
   )
   m = await channel.send("Text is required when sending buttons, unfortunately.", components=components)

Then for all button types other than :attr:`ButtonStyle.LINK`, you can get notified when a user clicks on your button. This is dispatched as a :code:`button_click` event, but for ease-of-use is also implemented into your sendable.

.. code-block:: python

   p = await m.wait_for_component_interaction()

.. note::

   The :func:`wait_for_component_interaction` function takes the same parameters as :func:`discord.Client.wait_for`.

.. warning::

   The :func:`wait_for_component_interaction` function will only work with the first :class:`voxelbotutils.MinimalBot` instance you create. If you are using multiple bot instances in the same script, use :func:`discord.Client.wait_for` as normal.

After that, you can work out which of your buttons the user clicked on and take action based on that, sending back to the button payload so as to complete the interaction.

.. code-block:: python

   clicked_button = p.component
   if clicked_button == button1:
      await p.send("You clicked on button 1!", ephemeral=True)
   elif clicked_button == button2:
      await p.send("You clicked on button 2!", ephemeral=True)
