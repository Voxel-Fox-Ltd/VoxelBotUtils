import asyncio
import typing

import discord
from discord.ext import commands

from .errors import InvokedMetaCommand


class SettingsMenuError(commands.CommandError):
    pass


class SettingsMenuOption(object):
    """
    An option that can be chosen for a settings menu's selectable item,
    eg an option that refers to a sub-menu, or a setting that refers to grabbing
    a role list, etc.
    """

    def __init__(
            self, ctx:commands.Context, display:typing.Union[str, typing.Callable[[commands.Context], str]],
            converter_args:typing.List[typing.Tuple]=list(),
            callback:typing.Callable[['SettingsMenuOption', typing.List[typing.Any]], None]=lambda x: None,
            emoji:str=None, allow_nullable:bool=True):
        """
        Args:
            ctx (commands.Context): The context for which the menu is being invoked.
            display (typing.Union[str, typing.Callable[[commands.Context], str]]): A string (or callable that returns string) that gives the display prompt for the option.
            converter_args (typing.List[typing.Tuple], optional): A list of tuples that should be used to convert the user-provided arguments. Tuples are passed directly into `convert_prompted_information`.
            callback (typing.Callable[['SettingsMenuOption', typing.List[typing.Any]], None], optional): A callable that's passed the information from the converter for you do to whatever with.
            emoji (str, optional): The emoji that this option refers to.
            allow_nullable (bool, optional): Whether or not this option is allowed to return None.
        """
        self.context: commands.Context = ctx
        self._display: typing.Union[str, typing.Callable[[commands.Context], str]] = display
        self.args: typing.List[typing.Tuple] = converter_args
        self.callback: typing.Callable[['SettingsMenuOption', typing.List[typing.Any]], None] = callback
        self.emoji: str = emoji
        self.allow_nullable: bool = allow_nullable

    def get_display(self) -> str:
        """
        Get the display prompt for this option.

        Returns:
            str: The string to be displayed
        """

        if isinstance(self._display, str):
            return self._display
        return self._display(self.context)

    async def perform_action(self) -> None:
        """
        Performs the stored action using the given args and kwargs.
        """

        # Get data
        returned_data = []
        for i in self.args:
            try:
                data = await self.convert_prompted_information(*i)
            except SettingsMenuError as e:
                if not self.allow_nullable:
                    raise e
                data = None
            returned_data.append(data)
            if data is None:
                break

        # Do callback
        if isinstance(self.callback, commands.Command):
            await self.callback.invoke(self.context)
        else:
            called_data = self.callback(self, *returned_data)
            if asyncio.iscoroutine(called_data):
                await called_data

    async def convert_prompted_information(self, prompt:str, asking_for:str, converter:commands.Converter, reactions:typing.List[discord.Emoji]=list()) -> typing.Any:
        """
        Ask the user for some information, convert it, and return that converted value to the user.

        Args:
            prompt (str): The text that we sent to the user -- something along the lines of "what channel do you want to use" etc.
            asking_for (str): Say what we're looking for them to send - doesn't need to be anything important, it just goes to the timeout message.
            converter (commands.Converter): The converter used to work out what to change the given user value to.
            reactions (typing.List[discord.Emoji], optional): The reactions that should be added to the prompt message.

        Returns:
            typing.Any: The converted information.

        Raises:
            InvokedMetaCommand: If converting the information timed out, raise this error to signal to the menu that we should exit.
            SettingsMenuError: If the converting failed for some other reason.
        """

        # Send prompt
        bot_message = await self.context.send(prompt)
        if reactions:
            for r in reactions:
                await bot_message.add_reaction(r)
        try:
            if reactions:
                user_message = None
                check = lambda r, u: r.message.id == bot_message.id and u.id == self.context.author.id and str(r.emoji) in reactions
                reaction, _ = await self.context.bot.wait_for("reaction_add", timeout=120, check=check)
                content = str(reaction.emoji)
            else:
                check = lambda m: m.channel.id == self.context.channel.id and m.author.id == self.context.author.id
                user_message = await self.context.bot.wait_for("message", timeout=120, check=check)
                content = user_message.content
        except asyncio.TimeoutError:
            await self.context.send(f"Timed out asking for {asking_for}.")
            raise InvokedMetaCommand()

        # Run converter
        conversion_failed = False
        if hasattr(converter, 'convert'):
            try:
                converter = converter()
            except TypeError:
                pass
            try:
                value = await converter.convert(self.context, content)
            except commands.CommandError:
                value = None
                conversion_failed = True
        else:
            try:
                value = converter(content)
            except Exception:
                value = None
                conversion_failed = True

        # Delete prompt messages
        try:
            await bot_message.delete()
        except discord.NotFound:
            pass
        try:
            await user_message.delete()
        except (discord.Forbidden, discord.NotFound, AttributeError):
            pass

        # Check conversion didn't fail
        if conversion_failed:
            raise SettingsMenuError()

        # Return converted value
        return value

    @classmethod
    def get_guild_settings_mention(cls, ctx:commands.Context, attr:str, default:str='none') -> str:
        """
        Get an item from the bot's guild settings.

        Args:
            ctx (commands.Context): The context for the command.
            attr (str): The attribute we want to mention.
            default (str, optional): If not found, what should the default be.

        Returns:
            str: The mention string.
        """

        settings = ctx.bot.guild_settings[ctx.guild.id]
        return cls.get_settings_mention(ctx, settings, attr, default)

    @classmethod
    def get_user_settings_mention(cls, ctx:commands.Context, attr:str, default:str='none') -> str:
        """
        Get an item from the bot's user settings.

        Args:
            ctx (commands.Context): The context for the command.
            attr (str): The attribute we want to mention.
            default (str, optional): If not found, what should the default be.

        Returns:
            str: The mention string.
        """

        settings = ctx.bot.user_settings[ctx.author.id]
        return cls.get_settings_mention(ctx, settings, attr, default)

    @classmethod
    def get_settings_mention(cls, ctx:commands.Context, settings:dict, attr:str, default:str='none') -> str:
        """
        Get an item from the bot's settings.

        Args:
            ctx (commands.Context): The context for the command.
            settings (dict): The dictionary with the settings in it that we want to grab.
            attr (str): The attribute we want to mention.
            default (str, optional): If not found, what should the default be.

        Returns:
            str: The mention string.
        """

        # Run converters
        if 'channel' in attr.lower().split('_'):
            data = ctx.bot.get_channel(settings[attr])
        elif 'role' in attr.lower().split('_'):
            data = ctx.guild.get_role(settings[attr])
        else:
            data = settings[attr]
            if isinstance(data, bool):
                return str(data).lower()
            return data

        # Get mention
        return cls.get_mention(data, default)

    @staticmethod
    def get_mention(data:typing.Union[discord.abc.GuildChannel, discord.Role, None], default:str) -> str:
        """
        Get the mention of an object.

        Args:
            data (typing.Union[discord.abc.GuildChannel, discord.Role, None]): The object we want to mention.
            default (str): The default string that should be output if we can't mention the object.

        Returns:
            str: The mention string.
        """

        mention = data.mention if data else default
        return mention

    @staticmethod
    def get_set_guild_settings_callback(table_name:str, column_name:str, serialize_function:typing.Callable[[typing.Any], typing.Any]=lambda x: x) -> typing.Callable[[dict], None]:
        """Return an async method that takes the data retuend by convert_prompted_information and then
        saves it into the database - should be used for the add_option stuff in the SettingsMenu init

        Args:
            table_name (str): The name of the table the data should be inserted into. This is not used when caching information. This should NOT be a user supplied value.
            column_name (str): The name of the column that the data should be inserted into. This is the same name that's used for caching. This should NOT be a user supplied value.
            serialize_function (typing.Callable[[typing.Any], typing.Any], optional): The function that is called to convert the input data in the callback into a database-friendly value. This is _not_ called for caching the value, only for databasing. The default serialize function doesn't do anything, but is provided so you don't have to provide one yourself.

        Returns:
            typing.Callable[[dict], None]: A callable function that sets the guild settings when provided with data
        """

        async def callback(self, data):
            """
            The function that actually sets the data in the specified table in the database.
            Any input to this function should be a direct converted value from `convert_prompted_information`.
            If the input is a discord.Role or discord.TextChannel, it is automatcally converted to that value's ID,
            which is then put into the datbase and cache.
            """

            if isinstance(data, (discord.Role, discord.TextChannel)):
                data = data.id
            original_data, data = data, serialize_function(data)

            async with self.context.bot.database() as db:
                await db(
                    "INSERT INTO {0} (guild_id, {1}) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET {1}=$2".format(table_name, column_name),
                    self.context.guild.id, data
                )
            self.context.bot.guild_settings[self.context.guild.id][column_name] = original_data
        return callback

    @staticmethod
    def get_set_user_settings_callback(table_name:str, column_name:str, serialize_function:typing.Callable[[typing.Any], typing.Any]=lambda x: x) -> typing.Callable[[dict], None]:
        """
        Return an async method that takes the data retuend by convert_prompted_information and then
        saves it into the database - should be used for the add_option stuff in the SettingsMenu init.

        Args:
            table_name (str): The name of the table the data should be inserted into. This is not used when caching information. This should NOT be a user supplied value.
            column_name (str): The name of the column that the data should be inserted into. This is the same name that's used for caching the value. This should NOT be a user supplied value.
            serialize_function (typing.Callable[[typing.Any], typing.Any], optional): The function that is called to convert the input data in the callback into a database-friendly value. This is _not_ called for caching the value, only for databasing. The default serialize function doesn't do anything, but is provided so you don't have to provide one yourself.

        Returns:
            typing.Callable[[dict], None]: A callable function that sets the user settings when provided with data
        """

        async def callback(self, data):
            """
            The function that actually sets the data in the specified table in the database.
            Any input to this function should be a direct converted value from `convert_prompted_information`.
            If the input is a discord.Role or discord.TextChannel, it is automatcally converted to that value's ID,
            which is then put into the datbase and cache.
            """

            if isinstance(data, (discord.Role, discord.TextChannel)):
                data = data.id
            original_data, data = data, serialize_function(data)

            async with self.context.bot.database() as db:
                await db(
                    "INSERT INTO {0} (user_id, {1}) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET {1}=$2".format(table_name, column_name),
                    self.context.author.id, data
                )
            self.context.bot.user_settings[self.context.author.id][column_name] = original_data
        return callback

    @staticmethod
    def get_set_iterable_delete_callback(table_name:str, column_name:str, cache_key:str, database_key:str) -> typing.Callable:
        """
        Return an async method that takes the data retuend by convert_prompted_information and then
        saves it into the database - should be used for the add_option stuff in the SettingsMenu init.

        Args:
            table_name (str): The name of the database that you want to remove data from.
            column_name (str): The column name that the key is inserted into in the table.
            cache_key (str): The key that's used to access the cached value for the iterable in `bot.guilds_settings`.
            database_key (str): The key that's used to refer to the role ID in the `role_list` table.

        Returns:
            typing.Callable: A callable for `SettingsMenuIterable` objects to use.
        """

        def wrapper(menu, ctx, role_id:int):
            async def callback(menu):
                """
                The function that actually deletes the role from the database
                Any input to this function will be silently discarded, since the actual input to this function is defined
                in the callback definition
                """

                # Database it
                async with ctx.bot.database() as db:
                    await db(
                        "DELETE FROM {0} WHERE guild_id=$1 AND {1}=$2 AND key=$3".format(table_name, column_name),
                        ctx.guild.id, role_id, database_key
                    )

                # Cache it
                try:
                    ctx.bot.guild_settings[ctx.guild.id][cache_key].remove(role_id)
                except AttributeError:
                    ctx.bot.guild_settings[ctx.guild.id][cache_key].pop(role_id)
            return callback
        return wrapper

    @staticmethod
    def get_set_iterable_add_callback(table_name:str, column_name:str, cache_key:str, database_key:str, serialize_function:typing.Callable[[typing.Any], str]=lambda x: x) -> typing.Callable:
        """
        Return an async method that takes the data retuend by convert_prompted_information and then
        saves it into the database - should be used for the add_option stuff in the SettingsMenu init.

        Args:
            table_name (str): The name of the database that you want to add data to.
            column_name (str): The column name that the key is inserted into in the table.
            cache_key (str): This is the key that's used when caching the value in `bot.guild_settings`.
            database_key (str): This is the key that the value is added to the database table `role_list`.
            serialize_function (typing.Callable[[typing.Any], str], optional): The function run on the value to convert it into to make it database-safe. Values are automatically cast to strings after being run through the serialize function. The serialize_function is called when caching the value, but the cached value is not cast to a string. The default serialize function doesn't do anything, but is provided so you don't have to provide one yourself.

        Returns:
            typing.Callable: A callable for `SettingsMenuIterable` objects to use.
        """

        def wrapper(menu, ctx):
            async def callback(menu, *data):
                """
                The function that actually adds the role to the table in the database
                Any input to this function will be direct outputs from perform_action's convert_prompted_information
                This is a function that creates a callback, so the expectation of `data` in this instance is that data is either
                a list of one item for a listing, eg [role_id], or a list of two items for a mapping, eg [role_id, value]
                """

                # Unpack the data
                try:
                    role, original_value = data
                    value = str(serialize_function(original_value))
                except ValueError:
                    role, value = data[0], None

                # Database it
                async with ctx.bot.database() as db:
                    await db(
                        """INSERT INTO {0} (guild_id, {1}, key, value) VALUES ($1, $2, $3, $4)
                        ON CONFLICT (guild_id, {1}, key) DO UPDATE SET value=excluded.value""".format(table_name, column_name),
                        ctx.guild.id, role.id, database_key, value
                    )

                # Cache it
                if value:
                    ctx.bot.guild_settings[ctx.guild.id][cache_key][role.id] = serialize_function(original_value)
                else:
                    if role.id not in ctx.bot.guild_settings[ctx.guild.id][cache_key]:
                        ctx.bot.guild_settings[ctx.guild.id][cache_key].append(role.id)
            return callback
        return wrapper


class SettingsMenu(object):
    """
    A settings menu object for setting up sub-menus or bot settings.
    Each menu object must be added as its own command, with sub-menus being.
    referred to by string in the MenuItem's action.
    """

    TICK_EMOJI = "\N{HEAVY CHECK MARK}"
    PLUS_EMOJI = "\N{HEAVY PLUS SIGN}"

    def __init__(self):
        self.options: typing.List[SettingsMenuOption] = list()
        self.emoji_options: typing.Dict[str, SettingsMenuOption] = {}

    def add_option(self, option:SettingsMenuOption):
        """
        Add an option to the settings list.
        """

        self.options.append(option)

    def bulk_add_options(self, ctx:commands.Context, *args):
        """
        Add MULTIPLE options to the settings list.
        Each option is simply thrown into a SettingsMenuOption item and then added to the options list.
        """

        for data in args:
            self.add_option(SettingsMenuOption(ctx, **data))

    async def start(self, ctx:commands.Context, *, timeout:float=120, clear_reactions_on_loop:bool=False):
        """
        Start the menu running.

        Args:
            ctx (commands.Context): The context object for the called command.
            timeout (float, optional): How long the bot should wait for a reaction.
            clear_reactions_on_loop (bool, optional): Exactly as it says - when the menu loops, should reactions be cleared? You only need to set this to True if the items in a menu change on loop.
        """

        message = None
        while True:

            # Send message
            self.emoji_options.clear()
            data, emoji_list = self.get_sendable_data(ctx)
            sent_new_message = False
            if message is None:
                message = await ctx.send(**data)
                sent_new_message = True
            else:
                await message.edit(**data)
            if sent_new_message or clear_reactions_on_loop:
                for e in emoji_list:
                    await message.add_reaction(e)

            # Get the reaction
            try:
                check = lambda r, u: u.id == ctx.author.id and r.message.id == message.id
                reaction, _ = await ctx.bot.wait_for("reaction_add", check=check, timeout=timeout)
            except asyncio.TimeoutError:
                break
            picked_emoji = str(reaction.emoji)

            # Get the picked option
            try:
                picked_option = self.emoji_options[picked_emoji]
            except KeyError:
                continue

            # Process the picked option
            if picked_option is None:
                break
            try:
                await picked_option.perform_action()
            except SettingsMenuError:
                pass

            # Remove the emoji
            try:
                if clear_reactions_on_loop:
                    await reaction.message.clear_reactions()
                else:
                    await reaction.message.remove_reaction(picked_emoji, ctx.author)
            except discord.Forbidden:
                pass
            except discord.NotFound:
                break

        # Delete all the processing stuff
        try:
            await message.delete()
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

    def get_sendable_data(self, ctx:commands.Context) -> typing.Tuple[dict, typing.List[str]]:
        """
        Get a valid set of sendable data for the destination.

        Args:
            ctx (commands.Context): Just so we can set the invoke meta flag.

        Returns:
            typing.Tuple[dict, typing.List[str]]: A tuple of the sendable data for the destination that can be unpacked into a `discord.abc.Messageable.send`, and a list of emoji to add to the message in question.
        """

        ctx.invoke_meta = True

        # Create embed
        embed = discord.Embed()
        lines = []
        emoji_list = []
        index = 0
        for index, i in enumerate(self.options):
            emoji = i.emoji
            if emoji is None:
                emoji = f"{index}\N{COMBINING ENCLOSING KEYCAP}"
                index += 1
            display = i.get_display()
            if display:
                lines.append(f"{emoji} {i.get_display()}")
            self.emoji_options[emoji] = i
            emoji_list.append(emoji)

        # Finish embed
        text_lines = '\n'.join(lines)
        embed.description = text_lines or "No set data"

        # Add tick
        self.emoji_options[self.TICK_EMOJI] = None
        emoji_list.append(self.TICK_EMOJI)

        # Return data
        return {'embed': embed}, emoji_list


class SettingsMenuIterableBase(SettingsMenu):
    """
    This is the base for the settings menu iterable.
    """

    def __init__(
            self, cache_key:str, key_display_function:typing.Callable[[typing.Any], str]=None, value_display_function:typing.Callable[[typing.Any], str]=str,
            *, iterable_add_callback:typing.Callable=None, iterable_delete_callback:typing.Callable=None, max_iterable_count:int=10):
        """
        Args:
            cache_key (str): The key used to grab the cached data from the `bot.guild_settings`.
            key_display_function (typing.Callable[[typing.Any], str], optional): The function used to display the data provided from the cache. Something like `guild.get_role(key).name`.
            value_display_function (typing.Callable[[typing.Any], str], optional): The function used to display the data provided from the cache. Something like `guild.get_role(key).name`. Not necessary if the cached item is a _list_ rather than a dict.
            iterable_add_callback (typing.Callable, optional): A callable used to cache and store the given converted item. The provided arguments to this function are the settings menu intstance, and the command context. It should return another callable that takes a list of the converted items.
            iterable_delete_callback (typing.Callable, optional): A callable used to uncache and delete the given item. The provided arguments to this function are the settings menu intstance, the command context, and the item that the iterable should refer to. It should return a callable with no arguments that performs the action.
            max_iterable_count (int, optional): The maximum amount of items that are allowed on the iterables menu.
        """

        super().__init__()

        self.cache_key = cache_key
        self.key_display_function = key_display_function or (lambda x: x)
        self.value_display_function = value_display_function or (lambda x: x)

        self.iterable_add_callback = iterable_add_callback
        self.iterable_delete_callback = iterable_delete_callback

        self.max_iterable_count = max_iterable_count

        self.convertable_values = []

    def add_convertable_value(self, prompt:str=None, converter:commands.Converter=str) -> None:
        """
        Add a convertable value to the convertable value list.

        Args:
            prompt (str, optional): The text sent to the user when the bot asks them to input some data.
            converter (commands.Converter, optional): The converter object used to convert the provided user value into something usable.
        """

        self.convertable_values.append((prompt, "value", converter))

    def bulk_add_convertable_value(self, ctx:commands.Context, *args):
        """
        Add MULTIPLE options to the settings list.
        Each option is simply thrown into a SettingsMenuOption item and then added to the options list.
        """

        for data in args:
            self.add_convertable_value(*data)

    def get_sendable_data(self, ctx:commands.Context):

        # Get the current data
        data_points = ctx.bot.guild_settings[ctx.guild.id][self.cache_key]

        # Current data is a key-value pair
        if isinstance(data_points, dict):
            self.options = [
                SettingsMenuOption(
                    ctx, f"{self.key_display_function(i)!s} - {self.value_display_function(o)!s}", (),
                    self.iterable_delete_callback(self, ctx, i), allow_nullable=False,
                )
                for i, o in data_points.items()
            ]
            if len(self.options) < self.max_iterable_count:
                self.options.append(
                    SettingsMenuOption(
                        ctx, "", self.convertable_values,
                        self.iterable_add_callback(self, ctx),
                        emoji=self.PLUS_EMOJI,
                        allow_nullable=False,
                    )
                )

        # Current data is a key list
        elif isinstance(data_points, list):
            self.options = [
                SettingsMenuOption(
                    ctx, f"{self.key_display_function(i)!s}", (),
                    self.iterable_delete_callback(self, ctx, i),
                    allow_nullable=False,
                )
                for i in data_points
            ]
            if len(self.options) < self.max_iterable_count:
                self.options.append(
                    SettingsMenuOption(
                        ctx, "", self.convertable_values,
                        self.iterable_add_callback(self, ctx),
                        emoji=self.PLUS_EMOJI,
                        allow_nullable=False,
                    )
                )

        # Generate the data as normal
        return super().get_sendable_data(ctx)

    async def start(self, *args, clear_reactions_on_loop:bool=True, **kwargs):
        return await super().start(*args, clear_reactions_on_loop=clear_reactions_on_loop, **kwargs)


class SettingsMenuIterable(SettingsMenu):
    """
    A version of the settings menu for dealing with things like lists and dictionaries
    that are just straight read/stored in the database.
    """

    def __init__(
            self, table_name:str, column_name:str, cache_key:str, database_key:str,
            key_converter:commands.Converter, key_prompt:str, key_display_function:typing.Callable[[typing.Any], str],
            value_converter:commands.Converter=str, value_prompt:str=None, value_serialize_function:typing.Callable=None,
            *, iterable_add_callback:typing.Callable=None, iterable_delete_callback:typing.Callable=None):
        """
        Args:
            table_name (str): The name of the table that the data should be inserted into.
            column_name (str): The column name for the table where teh key should be inserted to.
            cache_key (str): The key that goes into `bot.guild_settings` to get to the cached iterable.
            database_key (str): The key that would be inserted into the default `role_list` or `channel_list` tables.
            key_converter (commands.Converter): The converter that's used to take the user's input and convert it into a given object. Usually this will be a `discord.ext.commands.RoleConverter` or `discord.ext.commands.TextChannelConverter`.
            key_prompt (str): The string send to the user when asking for the key.
            key_display_function (typing.Callable[[typing.Any], str]): A function used to take the raw data from the key and change it into a display value.
            value_converter (commands.Converter, optional): The converter that's used to take the user's input and change it into something of value.
            value_prompt (str, optional): The string send to the user when asking for the value.
            value_serialize_function (typing.Callable, optional): A function used to take the converted value and change it into something database-friendly.
            iterable_add_callback (typing.Callable, optional): A function that's run with the params of the database name, the column name, the cache key, the database key, and the value serialize function. If left blank then it defaults to making a new callback for you that just adds to the `role_list` or `channel_list` table as specified.
            iterable_delete_callback (typing.Callable, optional): A function that's run with the params of the database name, the column name, the item to be deleted, the cache key, and the database key. If left blank then it defaults to making a new callback for you that just deletes from the `role_list` or `channel_list` table as specified.
        """
        super().__init__()

        # Set up the storage data
        self.table_name = table_name
        self.column_name = column_name
        self.cache_key = cache_key
        self.database_key = database_key

        # Key conversion
        self.key_converter = key_converter
        self.key_prompt = key_prompt
        self.key_display_function = key_display_function

        # Value conversion
        self.value_converter = value_converter
        self.value_prompt = value_prompt
        self.value_serialize_function = value_serialize_function or (lambda x: x)

        # Callbacks
        self.iterable_add_callback = iterable_add_callback or SettingsMenuOption.get_set_iterable_add_callback(table_name, column_name, cache_key, database_key, value_serialize_function)
        self.iterable_delete_callback = iterable_delete_callback or SettingsMenuOption.get_set_iterable_delete_callback(table_name, column_name, cache_key, database_key)

    def get_sendable_data(self, ctx:commands.Context):
        """Create a list of mentions from the given guild settings key, creating all relevant callbacks"""

        # Get the current data
        data_points = ctx.bot.guild_settings[ctx.guild.id][self.cache_key]

        # Current data is a key-value pair
        if isinstance(data_points, dict):
            self.options = [
                SettingsMenuOption(
                    ctx, f"{self.key_display_function(i)} - {self.value_converter(o)!s}", (),
                    self.iterable_delete_callback(self.table_name, self.column_name, i, self.cache_key, self.database_key),
                    allow_nullable=False,
                )
                for i, o in data_points.items()
            ]
            if len(self.options) < 10:
                self.options.append(
                    SettingsMenuOption(
                        ctx, "", [
                            (self.key_prompt, "value", self.key_converter),
                            (self.value_prompt, "value", self.value_converter)
                        ], self.iterable_add_callback(self.table_name, self.column_name, self.cache_key, self.database_key, self.value_serialize_function),
                        emoji=self.PLUS_EMOJI,
                        allow_nullable=False,
                    )
                )

        # Current data is a key list
        elif isinstance(data_points, list):
            self.options = [
                SettingsMenuOption(
                    ctx, f"{self.key_display_function(i)}", (),
                    self.iterable_delete_callback(self.table_name, self.column_name, i, self.cache_key, self.database_key),
                    allow_nullable=False,
                )
                for i in data_points
            ]
            if len(self.options) < 10:
                self.options.append(
                    SettingsMenuOption(
                        ctx, "", [
                            (self.key_prompt, "value", self.key_converter),
                        ], self.iterable_add_callback(self.table_name, self.column_name, self.cache_key, self.database_key),
                        emoji=self.PLUS_EMOJI,
                        allow_nullable=False,
                    )
                )

        # Generate the data as normal
        return super().get_sendable_data(ctx)
