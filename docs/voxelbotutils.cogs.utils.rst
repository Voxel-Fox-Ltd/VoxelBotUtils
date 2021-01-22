Utils
================================

Embed
----------------------------------------------

.. autoclass:: voxelbotutils.Embed
   :members:

   .. note::
      All of the methods and attributes available in :ref:`discord.Embed` still work as they did before; nothing has had any breaking changes.

   .. code-block:: python

      # I'm using a context block here, but that's entirely optional - assigning e to Embed() still works just fine
      with voxelbotutils.Embed(use_random_colour=True) as e:
         # Adding fields now doesn't need kwargs
         e.add_field("Test", "Post")
         e.add_field("Please", "Ignore")

         # You can set author to a user instead of having to deal with the default `.set_author`
         e.set_author_to_user(bot.get_user(141231597155385344))

         # You can now edit a field by it's name - doing this requires kwargs, non-mentioned fields stay the same
         e.edit_field_by_key("Test", name="New Test!", value="Whatever")

         # All of the methods also return themselves, so you can chain them if you really want to
         e.add_field("A", "B").add_field("C", "D")

      # And of course you still send it as it was
      await channel.send(embed=e)

Bot
-------------------------------------------

.. autoclass:: voxelbotutils.Bot
   :members:
   :no-inherited-members:
   :no-members: close, invoke, login, start

Cog
-------------------------------------------

.. autoclass:: voxelbotutils.Cog
   :members:

   Almost everything is still the same as the defaul discord.py cog. Notable changes: `Cog.logger` is a thing - that's a deafult logger that follows the same loglevel as `Bot.logger`; `Cog.cache_setup` is a new awaitable method that's run at bot startup - use it to set up your cache values should you need them, but otherwise you should just pull from your database tbh.

Command
-----------------------------------------------

.. autoclass:: voxelbotutils.Command
   :members:

.. autoclass:: voxelbotutils.Group
   :members:

voxelbotutils.Context
-----------------------------------------------

.. autoclass:: voxelbotutils.Context
   :members:

DatabaseConnection
----------------------------------------

.. autoclass:: voxelbotutils.DatabaseConnection
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

RedisConnection
-------------------------------------

.. autoclass:: voxelbotutils.RedisConnection
   :members:

   .. note::
      This is only enabled if redis is enabled in the config.

StatsdConnection
-------------------------------------

.. autoclass:: voxelbotutils.StatsdConnection
   :members:

TimeValue
-------------------------------------------

.. autoclass:: voxelbotutils.TimeValue
   :members:

   .. note::
       This util is also available as an argument converter for your commands, though it can be used outide of being a converter as well via use of the `.parse` classmethod.

   .. code-block:: python

      >>> value = voxelbotutils.TimeValue(606)
      >>> value.clean
      '10m6s'
      >>> value.clean_spaced
      '10m 6s'
      >>> value = voxelbotutils.TimeValue.parse('10m6s')
      >>> value.duration
      606
