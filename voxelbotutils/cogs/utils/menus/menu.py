from __future__ import annotations

import asyncio
import typing
import inspect

import discord
from discord.ext import commands

from .errors import ConverterTimeout
from .option import Option
from .mixins import MenuDisplayable
from .callbacks import MenuCallbacks
from .converter import Converter
from ..custom_cog import Cog
from ..custom_command import Command

if typing.TYPE_CHECKING:
    ContextCallable = typing.Callable[[commands.Context], None]
    AwaitableContextCallable = typing.Awaitable[ContextCallable]
    MaybeCoroContextCallable = typing.Union[ContextCallable, AwaitableContextCallable]


def _do_nothing(return_value=None):
    def wrapper(*args, **kwargs):
        if return_value:
            return return_value()
        return return_value
    return wrapper


class Menu(MenuDisplayable):
    """
    A menu using components that's meant to ease up the process of doing settings within your bot.
    """

    callbacks = MenuCallbacks

    def __init__(
            self, *options: Option, display: str = None, component_display: str = None):
        """
        Args:
            options (typing.List[Option]): A list of options that should be displayed in the menu.
            display (str, optional): When using a nested submenu, this is the option that should be displayed.
            component_display (str, optional): When using a nested submenu, this is the option that
                should be displayed in the component.
        """

        self.display = display  # Used for nested menus
        self.component_display = component_display  # Used for nested menus
        self._options = list(options)

    def create_cog(
            self, bot=None, *, cog_name: str = "Bot Settings", name: str = "settings",
            aliases: typing.List[str] = ["setup"], permissions: typing.List[str] = None,
            post_invoke: MaybeCoroContextCallable = None, **command_kwargs) -> typing.Union[commands.Cog, typing.Type[commands.Cog]]:
        """
        Creates a cog that can be loaded into the bot in a setup method.

        Args:
            bot: The bot object. If given, the cog will be instantiated with that object.
            cog_name (str, optional): The name of the cog to be added.
            name (str, optional): The name of the command to be added.
            aliases (typing.List[str], optional): A list of aliases to be added to the settings command.
            permissions (typing.List[str]): A list of permission names should be required for the command run.
            post_invoke (typing.Union[typing.Callable[[commands.Context], None], typing.Awaitable[typing.Callable[[commands.Context], None]]]): A
                post-invoke method that can be called.
        """

        permissions = permissions if permissions is not None else ["manage_guild"]

        class NestedCog(Cog, name=cog_name):

            def cog_unload(self):
                self.bot.remove_command(name)
                super().cog_unload()

            @commands.command(cls=Command, name=name, aliases=aliases, **command_kwargs)
            @commands.has_permissions(**{i: True for i in permissions})
            @commands.bot_has_permissions(send_messages=True, embed_links=True)
            async def settings(nested_self, ctx):
                """
                Modify some of the bot's settings.
                """

                await self.start(ctx)
                if post_invoke is None:
                    return
                if inspect.iscoroutine(post_invoke):
                    await post_invoke(ctx)
                else:
                    post_invoke(ctx)

        if bot:
            return NestedCog(bot)
        return NestedCog

    async def get_options(self, ctx: commands.Context, force_regenerate: bool = False) -> typing.List[Option]:
        """
        Get all of the options for an instance.
        This method has an open database instance in :code:`ctx.database`.
        """

        return self._options

    async def start(self, ctx: commands.Context, delete_message: bool = False) -> None:
        """
        Run the menu instance.

        Args:
            ctx (commands.Context): A context object to run the settings menu from.
            delete_messages (bool, optional): Whether or not to delete the menu when the user says
                they're done.
        """

        # Set up our base case
        sendable_data: dict = await self.get_sendable_data(ctx)
        sent_components: discord.ui.MessageComponents = sendable_data['components']
        menu_message: discord.Message = await ctx.send(**sendable_data)

        # Set up a function so as to get
        def get_button_check(given_message):
            def button_check(payload):
                if payload.message.id != given_message.id:
                    return False
                if payload.user.id == ctx.author.id:
                    return True
                ctx.bot.loop.create_task(payload.respond(f"Only {ctx.author.mention} can interact with these buttons.", ephemeral=True))
                return False
            return button_check

        # Keep looping while we're expecting a user input
        while True:

            # Wait for the user to click on a button
            try:
                payload = await ctx.bot.wait_for("component_interaction", check=get_button_check(menu_message), timeout=60.0)
                await payload.response.defer_update()
            except asyncio.TimeoutError:
                break

            # Determine the option they clicked for
            clicked_option = None
            options = await self.get_options(ctx)
            for i in options:
                if i.component_display == payload.component.label:
                    clicked_option = i
                    break
            if clicked_option is None:
                break

            # Run the given option
            try:
                if clicked_option.converters or isinstance(clicked_option._callback, Menu):
                    await menu_message.edit(components=sent_components.disable_components())
                if isinstance(clicked_option._callback, Menu):
                    await clicked_option._callback.start(ctx, delete_message=True)
                else:
                    await clicked_option.run(ctx)
            except ConverterTimeout as e:
                await ctx.send(e.message)
                break
            except asyncio.TimeoutError:
                break

            # Edit the message with our new buttons
            sendable_data = await self.get_sendable_data(ctx)
            sent_components = sendable_data['components']
            await menu_message.edit(**sendable_data)

        # Disable the buttons before we leave
        try:
            if delete_message:
                await menu_message.delete()
            else:
                await menu_message.edit(components=sent_components.disable_components())
        except Exception:
            pass

    async def get_sendable_data(self, ctx: commands.Context) -> dict:
        """
        Gets a dictionary of sendable objects to unpack for the :func:`start` method.
        """

        # Make our output lists
        output_strings = []
        buttons = []

        # Add items to the list
        async with ctx.bot.database() as db:
            ctx.database = db
            options = await self.get_options(ctx, force_regenerate=True)
            for i in options:
                output = await i.get_display(ctx)
                if output:
                    output_strings.append(f"\N{BULLET} {output}")
                style = (discord.ui.ButtonStyle.secondary if isinstance(i._callback, Menu) else None) or i._button_style or discord.ui.ButtonStyle.primary
                buttons.append(discord.ui.Button(
                    label=i.component_display,
                    custom_id=i.component_display,
                    style=style,
                ))
        ctx.database = None

        # Add a done button
        buttons.append(discord.ui.Button(label="Done", custom_id="Done", style=discord.ui.ButtonStyle.success))

        # Output
        components = discord.ui.MessageComponents.add_buttons_with_rows(*buttons)
        embed = discord.Embed(colour=0xffffff)
        embed.description = "\n".join(output_strings) or "No options added."
        return {
            "embed": embed,
            "components": components,
        }


class MenuIterable(Menu, Option):
    """
    A menu instance that takes and shows iterable data.
    """

    allow_none = False

    def __init__(
            self, *, select_sql: str, insert_sql: str, delete_sql: str,
            row_text_display: typing.Callable[[commands.Context, dict], str],
            row_component_display: typing.Callable[[commands.Context, dict], str],
            converters: typing.List[Converter],
            select_sql_args: typing.Callable[[commands.Context], typing.List[typing.Any]] = None,
            insert_sql_args: typing.Callable[[commands.Context, typing.List[typing.Any]], typing.List[typing.Any]] = None,
            delete_sql_args: typing.Callable[[commands.Context, dict], typing.List[typing.Any]] = None,
            cache_callback: typing.Optional[typing.Callable[[commands.Context, typing.List[typing.Any]], None]] = None,
            cache_delete_callback: typing.Optional[typing.Callable[[commands.Context, typing.List[typing.Any]], None]] = None,
            cache_delete_args: typing.Optional[typing.Callable[[dict], typing.List[typing.Any]]] = None):
        """
        Args:
            select_sql (str): The SQL that should be used to select the rows to be displayed from the database.
            select_sql_args (typing.Callable[[commands.Context], typing.List[typing.Any]]): A function returning a
                list of arguments that should be passed to the database select.
            insert_sql (str): The SQL that should be used to insert the data into the database.
            insert_sql_args (typing.Callable[[commands.Context, typing.List[typing.Any]], typing.List[typing.Any]]): A
                function returning a list of arguments that should be passed to the database insert.
            delete_sql (str): The SQL that should be used to delete a row from the database.
            delete_sql_args (typing.Callable[[commands.Context, dict], typing.List[typing.Any]]): A function returning a
                list of arguments that should be passed to the database delete.
            row_text_display (typing.Callable[[commands.Context, dict], str]): A function returning a string which should
                be showed in the menu.
            row_component_display (typing.Callable[[commands.Context, dict], str]): A function returning a string
                which should be shown on the component.
            converters (typing.List[Converter]): A list of converters that the user should be asked for.
            cache_callback (typing.Optional[typing.Callable[[commands.Context, typing.List[typing.Any]], None]]): Description
            cache_delete_callback (typing.Optional[typing.Callable[[commands.Context, typing.List[typing.Any]], None]]): Description
            cache_delete_args (typing.Optional[typing.Callable[[dict], typing.List[typing.Any]]]): Description
        """

        self.row_text_display = row_text_display
        self.row_component_display = row_component_display
        self.converters = converters

        self.cache_callback = cache_callback or _do_nothing()
        self.cache_delete_callback = cache_delete_callback or _do_nothing()
        self.cache_delete_args = cache_delete_args or _do_nothing()

        self.select_sql = select_sql
        self.select_sql_args = select_sql_args or _do_nothing(list)

        self.insert_sql = insert_sql
        self.insert_sql_args = insert_sql_args or _do_nothing(list)

        self.delete_sql = delete_sql
        self.delete_sql_args = delete_sql_args or _do_nothing(list)

        self._options = None

    def insert_database_call(self):
        """
        Run the insert database call.
        """

        async def wrapper(ctx, data):
            args = self.insert_sql_args(ctx, data)
            async with ctx.bot.database() as db:
                await db(self.insert_sql, *args)
        return wrapper

    def delete_database_call(self, row):
        """
        Run the delete database call.
        """

        async def wrapper(ctx, data):
            args = self.delete_sql_args(ctx, row)
            async with ctx.bot.database() as db:
                await db(self.delete_sql, *args)
        return wrapper

    async def get_options(self, ctx: commands.Context, force_regenerate: bool = False):
        """
        Get all of the options for an instance.
        This method has an open database instance in :code:`Context.database`.
        """

        # Let's not generate new ones if we don't need to
        if not force_regenerate and self._options is not None:
            return self._options

        # Grab our data from the database
        rows = await ctx.database(self.select_sql, *self.select_sql_args(ctx))
        generated = []

        # Make buttons for deleting the data
        for i in rows:
            v = Option(
                display=self.row_text_display(ctx, i),
                component_display=self.row_component_display(ctx, i),
                callback=self.delete_database_call(i),
                cache_callback=self.cache_delete_callback(*self.cache_delete_args(i))
            )
            v._button_style = discord.ui.ButtonStyle.danger
            generated.append(v)

        # Add "add new" button
        if len(generated) <= 20:
            v = Option(
                display=None,
                component_display="Add New",
                converters=self.converters,
                callback=self.insert_database_call(),
                cache_callback=self.cache_callback
            )
            v._button_style = discord.ui.ButtonStyle.secondary
            generated.append(v)

        # And return
        self._options = generated
        return generated
