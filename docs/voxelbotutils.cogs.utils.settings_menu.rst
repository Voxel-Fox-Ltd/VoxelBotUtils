Settings Menu
================================

How to
--------------------------------

Running one of these menus can be a *just a tad* unintuitive, so I'm putting an example on how to use it here.

.. code-block:: python

   # This creates a settings menu object
   menu = voxelbotutils.SettingsMenu()

   # This is just a shorthand function for getting a ping in the `bot.guild_settings` attr
   settings_mention = voxelbotutils.SettingsMenuOption.get_guild_settings_mention

   # Now we're gonna add options to our menu
   menu.add_option(
      voxelbotutils.SettingsMenuOption(
         ctx,

         # A function that returns a string to display
         display=lambda c: "Set setting (currently {0})".format(settings_mention(c, 'setting_id')),

         # A list of SettingsMenuConverter objects that should be used to convert the user inputs
         converter_args=[
            voxelbotutils.SettingsMenuConverter(
               prompt="What do you want to set the channel to?",
               asking_for="setting channel",
               converter=commands.TextChannelConverter,
            )
         ],

         # A callback that's used to add to the datbase and cache
         callback=voxelbotutils.SettingsMenuOption.get_set_settings_callback('guild_settings', 'guild_id', 'channel_id'),

         # Whether or not a null value is allowed (ie whether this value can be unset)
         allow_nullable=True,
      )
   )

   # Now we just run the menu
   await menu.start(ctx)

API Reference
--------------------------------

.. autoclass:: voxelbotutils.SettingsMenu
   :show-inheritance:

.. autoclass:: voxelbotutils.SettingsMenuIterable

.. autoclass:: voxelbotutils.SettingsMenuOption
