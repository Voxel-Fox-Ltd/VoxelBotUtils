Interactions Howto
##########################################

Interactions such as slash commands and buttons are some sexy lil additions to Discord. As such, you'll probably want to use them. Fortunately, VoxelBotUtils makes this pretty easy. Aside from the howto, there's a :ref:`full API reference<interactions>` on the main API reference page.

Responding to an Interaction
------------------------------------------

Interactions need to be responded to, or it shows as "this interaction has failed" in the Discord UI. The Discord API supports a few ways of responding:

* :func:`defer<voxelbotutils.InteractionMessageable.defer>` an interaction, which gives a "processing" message, and respond later.
* :func:`defer_update<voxelbotutils.InteractionMessageable.defer_update>` an interaction, which doesn't give a processing message, and respond later. This is only available on components.
* :func:`respond<voxelbotutils.InteractionMessageable.respond>` to an interaction, and receive no :class:`discord.Message` object back.

Slash Commands
------------------------------------------

One of the inbuilt cogs in VBU adds the :code:`!addslashcommands` owner-only command, which attempts to automatically add all public commands as slash commands.

A public command needs all of the three:

* It can't be a :func:`meta command<voxelbotutils.checks.meta_command>`.
* It can't be an :func:`owner only command<discord.ext.commands.is_owner>` command.
* It needs its :attr:`add_slash_command<voxelbotutils.Command.add_slash_command>` attribute set to `True` (as is the default).

Running the :code:`!addslashcommands` command will make your bot attempt to convert all of your arguments and bulk-add the commands to Discord. If this conversion fails, you'll be given a traceback of the error so you can see exactly where the issue stems from.

Most issues stem from using :class:`discord.ext.commands.Greedy`, misordering your optional arguments (they must appear at the end), using even *slightly* complex group commands, and using converters that don't stem from a commonly converted types (though in this instance you can add a :code:`SLASH_COMMAND_ARG_TYPE` attribute being an instance of :class:`voxelbotutils.ApplicationCommandOptionType` to your converter for the bot to use).

When adding arguments to a command, you're able to give descriptions to those arguments using :attr:`voxelbotutils.Command.argument_descriptions`.

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
   await channel.send(
      "Text is required - component-only messages aren't supported yet (July 2021)",
      components=components,
   )

Buttons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using buttons has been made pretty simple. First, you send your button to the user.

.. code-block:: python

   button1 = voxelbotutils.Button("Button 1", custsom_id="button 1")
   button2 = voxelbotutils.Button("Button 2", custsom_id="button 1")
   components = voxelbotutils.MessageComponents(
      voxelbotutils.ActionRow(button1, button2)
   )
   m = await channel.send("X", components=components)

Then for all button types other than :attr:`ButtonStyle.LINK`, you can get notified when a user clicks on your button. This is dispatched as a :code:`component_interaction` event.

.. code-block:: python

   payload = await bot.wait_for(
      "component_interaction",
      check=lambda p: p.message.id == m.id,
   )
   await payload.defer()

After that, you can work out which of your buttons the user clicked on using their custom IDs and take action based on that, sending back to the button payload so as to complete the interaction:

.. code-block:: python

   clicked_button = payload.component
   if clicked_button.custom_id == "button 1":
      await payload.respond("{payload.user.mention} clicked on button 1!")
   elif clicked_button.custom_id == "button 2":
      await payload.respond("{payload.user.mention} clicked on button 2!")

Select Menus
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dropdowns allow the user to select one or more options from a given set. Unlike buttons, you can only fit one select menu per action row.

.. code-block:: python

   components = voxelbotutils.MessageComponents(
      voxelbotutils.ActionRow(
         voxelbotutils.SelectMenu(
            custom_id="select menu",
            options=[
               voxelbotutils.SelectOption(label="Item 1", value="item1"),
               voxelbotutils.SelectOption(label="Item 2", value="item2"),
               voxelbotutils.SelectOption(label="Item 3", value="item3"),
            ]
         )
      )
   )
   m = await channel.send("X", components=components)

You'll then receive a :code:`component_interaction` event for every time the user updates their selected options, the values of which are passed on to you.

.. code-block:: python

   payload = await bot.wait_for(
      "component_interaction",
      check=lambda p: p.message.id == m.id,
   )
   # payload.values is a list of strings
   await payload.respond("{payload.user.mention} set {payload.values} in the select menu!")
