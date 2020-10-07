Utils
================================

voxelbotutils.ContextEmbed
----------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.context_embed.ContextEmbed
   :members:

   .. note::
      All of the methods and attributes available in `discord.Embed` still work as they did before; nothing has had any breaking changes.

   .. code-block:: python

      # I'm using a context block here, but that's entirely optional - assigning e to Embed() still works just fine
      with voxelbotutils.Embed(use_random_colour=True) as e:
         e.add_field("Test", "Post")
         e.add_field("Please", "Ignore")
         e.set_author_to_user(bot.get_user(141231597155385344))

voxelbotutils.Bot
-------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.custom_bot.CustomBot
   :members: set_default_presence, reload_config, load_all_extensions, get_uptime, get_invite_link, get_extensions, add_delete_button

voxelbotutils.Cog
-------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.custom_cog.CustomCog
   :members:

voxelbotutils.Command
-----------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.custom_command.CustomCommand
   :members:

.. autoclass:: voxelbotutils.cogs.utils.custom_command.CustomGroup
   :members:

voxelbotutils.Context
-----------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.custom_context.CustomContext
   :members:

voxelbotutils.DatabaseConnection
----------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.database.DatabaseConnection
   :members:

   .. note::
      This is only enabled if the database is enabled in the config.

   .. code-block:: python

      # The database can be used via context
      async with bot.database() as db:
         values = await db("SELECT user_id FROM user_settings WHERE enabled=$1", True)
      for row in values:
         print(row['user_id'])

      # Or you can get a connection object that you can pass around
      db = await bot.database.get_connection()
      await db("DELETE FROM user_settings")
      await db.disconnect()

voxelbotutils.RedisConnection
-------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.redis.RedisConnection
   :members:

   .. note::
      This is only enabled if redis is enabled in the config.


voxelbotutils.TimeValue
-------------------------------------------

.. autoclass:: voxelbotutils.cogs.utils.time_value.TimeValue
   :members:

   .. note::
       This util is also available as a converter, though it can be used independently as well.

   .. code-block:: python

      value = voxelbotutils.TimeValue(600)
      value.clean  # '10m'
      value = voxelbotutils.TimeValue.parse('10m')
      value.duration  # 600
