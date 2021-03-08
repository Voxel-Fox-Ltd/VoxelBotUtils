Settings Menu
================================

How to
--------------------------------

Running one of these menus can be a *just a tad* unintuitive, so I'm putting an example on how to use it here.

.. code-block:: python

   # This creates a settings menu object
   menu = voxelbotutils.SettingsMenu()

   # This is just a shorthand function for mentioning an item in the `bot.guild_settings` attr
   settings_mention = voxelbotutils.SettingsMenuOption.get_guild_settings_mention

   # Now we're gonna add options to our menu
   menu.add_option(
      voxelbotutils.SettingsMenuOption(
         ctx,

         # A function that returns a string to display
         display=lambda c: "Set setting (currently {0})".format(settings_mention(c, 'setting_id')),

         # A list of tuples to throw into the converter
         converter_args=[(
               # The prompt to send to the user
               "What do you want to set the setting to?",

               # A vague description of what you're asking for - only used in the timeout message
               "setting channel",

               # A converter instance that'll be used to convert the user input
               commands.TextChannelConverter,
         )],

         # A callback that's used to add to the datbase and cache
         callback=voxelbotutils.SettingsMenuOption.get_set_settings_callback('guild_settings', 'guild_id', 'setting_id'),

         # Whether or not a null value is allowed (ie whether this value can be unset)
         allow_nullable=True,
      )
   )

   # Now we just run the menu
   await menu.start(ctx)

Here's an in-use example from one of my projects:

.. code-block:: python

   @voxelbotutils.group()
   @commands.has_permissions(manage_guild=True)
   @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True)
   @commands.guild_only()
   async def setup(self, ctx:voxelbotutils.Context):
      """
      Run the bot setup.
      """

      # Make sure it's only run as its own command, not a parent
      if ctx.invoked_subcommand is not None:
         return

      # Create settings menu
      menu = voxelbotutils.SettingsMenu()
      settings_mention = voxelbotutils.SettingsMenuOption.get_guild_settings_mention
      menu.add_multiple_options(
         voxelbotutils.SettingsMenuOption(
            ctx,
            display=lambda c: "Set quote channel (currently {0})".format(settings_mention(c, 'quote_channel_id')),
            converter_args=[(
               "What do you want to set the quote channel to?",
               "quote channel",
               commands.TextChannelConverter
            )],
            callback=voxelbotutils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'quote_channel_id'),
         ),
         voxelbotutils.SettingsMenuOption(
            ctx,
            display="Nickname settings",
            callback=self.bot.get_command("setup nicknames"),
         ),
      )

      # Run the menu
      try:
         await menu.start(ctx)
         await ctx.send("Done setting up!")
      except voxelbotutils.errors.InvokedMetaCommand:
         pass

   @setup.command()
   @voxelbotutils.checks.meta_command()
   async def nicknames(self, ctx:voxelbotutils.Context):
      """
      Run the bot's nickname submenu setup.
      """

      # Make sure it's only run as its own command, not a parent
      if ctx.invoked_subcommand is not None:
         return

      # Create settings menu
      menu = voxelbotutils.SettingsMenu()
      settings_mention = voxelbotutils.SettingsMenuOption.get_guild_settings_mention
      menu.add_multiple_options(
         voxelbotutils.SettingsMenuOption(
            ctx,
            display=lambda c: "Set nickname change ban role (currently {0})".format(settings_mention(c, 'nickname_banned_role_id')),
            converter_args=[(
               "Which role should be set to stop users changing their nickname?",
               "nickname change ban role",
               commands.RoleConverter,
            )],
            callback=voxelbotutils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'nickname_banned_role_id'),
         )
      )

      # Run the menu
      await menu.start(ctx)

API Reference
--------------------------------

.. autoclass:: voxelbotutils.SettingsMenu
   :show-inheritance:

.. autoclass:: voxelbotutils.SettingsMenuIterable

.. autoclass:: voxelbotutils.SettingsMenuOption
