Settings Menu
================================

How to
--------------------------------

Running one of these menus can be a *just a tad* unintuitive, so I'm putting an example on how to use it here.

.. code-block:: python

   # This creates a settings menu object
   menu = voxelbotutils.SettingsMenu()

   # This is just a shorthand function for mentioning an item in the `bot.guild_settings` attr
   settings_mention = utils.SettingsMenuOption.get_guild_settings_mention

   # Now we're gonna add options to our menu
   menu.add_option(voxelbotutils.SettingsMenuOption(
      ctx=ctx,
      display=lambda c: "Set setting (currently {0})".format(settings_mention(c, 'setting_id')),
      converter_args=[("What do you want to set the setting to?", "setting channel", commands.TextChannelConverter,)],
      callback=voxelbotutils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'setting_id'),
      allow_nullable=True,
   ))

   # Now I'll go through them line-by-line:
   # * ctx is just a required argument for the option to run properly - it's used internally
   # * display can either be a string or a function that returns a string - it's the value that's shown on the menu
   # * converter_args should be a list/tuple OF 3-item list/tuples; the question that's asked to the user, the string to be shown if
   #   the timer runs out (eg "timed out asking for setting channel"), and a converter that's used after the user provides their input
   # * callback is a function that runs to be able to store the given user data - `voxelbotutils.SettingsMenuOption.get_set_guild_settings_callback`
   #   is a util that sets data into a given database (in this case it would insert the user data into guild_settings(setting_id)).
   #   You can set it to another command object to be able to use subcommands
   # * allow_nullable specifies if the given user data is allowed to be None

   # You can add multiple options at once via `menu.bulk_add_option`, where the only positional arg is `ctx`, and `*args` should be a dict of
   # kwargs for SettingsMenuOption

   # Now we just run the menu
   await menu.start(ctx)

Here's an in-use example from one of my projects:

.. code-block:: python

   @commands.group(cls=utils.Group)
   @commands.has_permissions(manage_guild=True)
   @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True)
   @commands.guild_only()
   async def setup(self, ctx:utils.Context):
      """Run the bot setup"""

      # Make sure it's only run as its own command, not a parent
      if ctx.invoked_subcommand is not None:
         return

      # Create settings menu
      menu = utils.SettingsMenu()
      settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
      menu.bulk_add_options(
         ctx,
         {
            'display': lambda c: "Set quote channel (currently {0})".format(settings_mention(c, 'quote_channel_id')),
            'converter_args': [("What do you want to set the quote channel to?", "quote channel", commands.TextChannelConverter)],
            'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'quote_channel_id'),
         },
         {
            'display': "Nickname settings",
            'callback': self.bot.get_command("setup nicknames"),
         },
      )
      try:
         await menu.start(ctx)
         await ctx.send("Done setting up!")
      except utils.errors.InvokedMetaCommand:
         pass

   @setup.command(cls=utils.Command)
   @utils.checks.meta_command()
   async def nicknames(self, ctx:utils.Context):
      """Run the bot setup"""

      # Make sure it's only run as its own command, not a parent
      if ctx.invoked_subcommand is not None:
         return

      # Create settings menu
      menu = utils.SettingsMenu()
      settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
      menu.bulk_add_options(
         ctx,
         {
            'display': lambda c: "Set nickname change ban role (currently {0})".format(settings_mention(c, 'nickname_banned_role_id')),
            'converter_args': [("Which role should be set to stop users changing their nickname?", "nickname change ban role", commands.RoleConverter)],
            'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'nickname_banned_role_id'),
         },
      )
      await menu.start(ctx)

API Reference
--------------------------------

.. autoclass:: voxelbotutils.SettingsMenu
   :members:
   :show-inheritance:

.. autoclass:: voxelbotutils.SettingsMenuIterable
   :members:

.. autoclass:: voxelbotutils.SettingsMenuOption
   :members:
