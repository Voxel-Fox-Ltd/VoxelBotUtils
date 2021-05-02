Utils
================================

Embed
----------------------------------------------

.. autoclass:: voxelbotutils.Embed

Bot
-------------------------------------------

.. autoclass:: voxelbotutils.Bot
   :exclude-members: close, invoke, login, start
   :no-inherited-members:

Cog
-------------------------------------------

.. autoclass:: voxelbotutils.Cog
   :no-special-members:

Command
-----------------------------------------------

.. autoclass:: voxelbotutils.Command

.. autoclass:: voxelbotutils.Group

Context
-----------------------------------------------

.. autoclass:: voxelbotutils.Context

DatabaseConnection
----------------------------------------

.. autoclass:: voxelbotutils.DatabaseConnection
   :no-special-members:

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

Paginator
-------------------------------------------

.. autoclass:: voxelbotutils.Paginator

   An automatic paginator util that takes a list and listens for reactions on a message to change the content.

   .. code-block:: python

      # Items will automatically be cast to strings and joined
      my_list = list(range(30))
      p = Paginator(my_list, per_page=5)
      await p.start(ctx, timeout=15)

      # Alternatively you can give a function, which can return a string, an embed, or a dict that gets unpacked directly
      # into the message's edit method
      def my_formatter(menu, items):
         output = []
         for i in items:
            output.append(f"The {i}th item")
         output_string = "\n".join(output)
         embed = voxelbotutils.Embed(description=output_string)
         embed.set_footer(f"Page {menu.current_page + 1}/{menu.max_pages}")

      p = Paginator(my_list, formatter=my_formatter)
      await p.start(ctx)

RedisConnection
-------------------------------------

.. autoclass:: voxelbotutils.RedisConnection
   :no-special-members:

   .. note::
      This is only enabled if redis is enabled in the config.

   Redis channels can be subscribed to via the use of the `redis_channel_handler` method;

   .. code-block:: python

      @redis_channel_handler("channel_name")
      async def handler(self, payload):
         self.logger.info(payload)

   You can publish data to them with the `publish` method:

   .. code-block:: python

      async with RedisConnection() as re:
         await re.publish("channel_name", {"foo": "bar"})
         await re.publish_str("channel_two", "baz")

StatsdConnection
-------------------------------------

.. autoclass:: voxelbotutils.StatsdConnection
   :no-special-members:

TimeValue
-------------------------------------------

.. autoclass:: voxelbotutils.TimeValue

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
