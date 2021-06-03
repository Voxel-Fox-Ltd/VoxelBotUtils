import typing
import asyncio
import inspect

import discord
from discord.ext import commands

from .context_embed import Embed
from .interactions.components import MessageComponents, Button, ButtonStyle, ActionRow


class Paginator(object):
    """
    An automatic paginator util that takes a list and listens for reactions on a message
    to change the content.

    ::

        # Items will automatically be cast to strings and joined
        my_list = list(range(30))
        p = voxelbotutils.Paginator(my_list, per_page=5)
        await p.start(ctx, timeout=15)

        # Alternatively you can give a function, which can return a string, an embed, or a dict
        # that gets unpacked directly into the message's edit method
        def my_formatter(menu, items):
            output = []
            for i in items:
                output.append(f"The {i}th item")
            output_string = "\\n".join(output)
            embed = voxelbotutils.Embed(description=output_string)
            embed.set_footer(f"Page {menu.current_page + 1}/{menu.max_pages}")

        p = voxelbotutils.Paginator(my_list, formatter=my_formatter)
        await p.start(ctx)
    """

    def __init__(
            self, data: typing.Union[typing.Sequence, typing.Generator, typing.Callable[[int], typing.Any]], *,
            per_page: int = 10,
            formatter: typing.Callable[
                ['Paginator', typing.Sequence[typing.Any]], typing.Union[str, discord.Embed, dict]
            ] = None,
            remove_reaction: bool = False):
        """
        Args:
            data (typing.Union[typing.Sequence, typing.Generator, typing.Callable[[int], typing.Any]]): The
                data that you want to paginate.
                If a generator or function is given then the `max_pages` will start as the string "?", and the `per_page`
                parameter will be ignored - the formatter will be passed the content of whatever your generator returns.
                If a function is given, then you will be passed the page number as an argument - raising
                `StopIteration` from this function will cause the `max_pages` attribute to be set,
                and the page will go back to what it was previously.
            per_page (int, optional): The number of items that appear on each page. This argument only works for sequences
            formatter (typing.Callable[['Paginator', typing.Sequence[typing.Any]], typing.Union[str, discord.Embed, dict]], optional): A
                function taking the paginator instance and a list of things to display, returning a dictionary of kwargs that get passed
                directly into a :func:`discord.Message.edit`.
        """
        self.data = data
        self.per_page = per_page
        self.formatter = formatter
        if self.formatter is None:
            self.formatter = self.default_list_formatter
        self.current_page = None
        self._page_cache = {}

        self.max_pages = '?'
        self._data_is_generator = any((
            inspect.isasyncgenfunction(self.data),
            inspect.isasyncgen(self.data),
            inspect.isgeneratorfunction(self.data),
            inspect.isgenerator(self.data),
        ))
        self._data_is_function = any((
            inspect.isfunction(self.data),
            inspect.iscoroutine(self.data),
        ))
        self._data_is_iterable = not (self._data_is_generator or self._data_is_function)
        if self._data_is_iterable:
            pages, left_over = divmod(len(data), self.per_page)
            if left_over:
                pages += 1
            self.max_pages = pages

    async def start(self, ctx: commands.Context, *, timeout: float = 120):
        """
        Start and handle a paginator instance.

        Args:
            ctx (commands.Context): The context instance for the called command.
            timeout (float, optional): How long you should wait between getting a reaction
                and timing out.
        """

        # Set our initial values
        self.current_page = 0
        if self.max_pages == 0:
            await ctx.send("There's no data to be shown.")
            return
        message = await ctx.send("Menu loading...")

        # Loop the reaction handler
        last_payload = None
        while True:

            # Get the page data
            try:
                items = await self.get_page(self.current_page)
            except (KeyError, IndexError):
                await message.edit(content="There's no data to be shown.")
                break

            # Format the page data
            payload = self.formatter(self, items)
            if isinstance(payload, discord.Embed):
                payload = {"embed": payload}
            elif isinstance(payload, str):
                payload = {"content": payload}

            # Set a default for these things
            payload.setdefault("content", None)
            payload.setdefault("embed", None)

            # Work out what components to show
            components = MessageComponents(
                ActionRow(
                    Button(
                        custom_id="START",
                        emoji="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}",
                        disabled=self.current_page == 0,
                    ),
                    Button(
                        custom_id="PREVIOUS",
                        emoji="\N{LEFTWARDS BLACK ARROW}",
                        style=ButtonStyle.SECONDARY,
                        disabled=self.current_page == 0,
                    ),
                    Button(
                        custom_id="STOP",
                        emoji="\N{BLACK SQUARE FOR STOP}",
                        style=ButtonStyle.DANGER,
                    ),
                    Button(
                        custom_id="NEXT",
                        emoji="\N{BLACK RIGHTWARDS ARROW}",
                        style=ButtonStyle.SECONDARY,
                        disabled=self.max_pages != "?" and self.current_page >= self.max_pages - 1,
                    ),
                    Button(
                        custom_id="END",
                        emoji="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}",
                        disabled=self.max_pages != "?" and self.current_page >= self.max_pages - 1,
                    ),
                )
            )

            # See if the content is unchanged
            if payload != last_payload:
                await message.edit(**payload, components=components)

            # See if we want to bother paginating
            last_payload = payload
            if self.max_pages == 1:
                return

            # Wait for reactions to be added by the user
            component_payload = None
            try:
                check = lambda p: p.user.id == ctx.author.id and p.message.id == message.id
                component_payload = await ctx.bot.wait_for("component_interaction", check=check, timeout=timeout)
                await component_payload.ack()
            except asyncio.TimeoutError:
                break

            # Change the page number based on the reaction
            if component_payload is None:
                self.current_page = "STOP"
            else:
                self.current_page = {
                    "START": lambda i: 0,
                    "PREVIOUS": lambda i: i - 1,
                    "STOP": lambda i: "STOP",
                    "NEXT": lambda i: i + 1,
                    "END": lambda i: self.max_pages,
                }[str(component_payload.component.custom_id)](self.current_page)
            if self.current_page == "STOP":
                break

            # Make sure the page number is still valid
            if self.max_pages != "?" and self.current_page >= self.max_pages:
                self.current_page = self.max_pages - 1
            elif self.current_page < 0:
                self.current_page = 0

        # Let us break from the loop
        ctx.bot.loop.create_task(message.edit(components=components.disable_components()))

    async def get_page(self, page_number: int) -> typing.List[typing.Any]:
        """
        Get a list of items that appear for a given page.

        Args:
            page_number (int): The page number to get.

        Returns:
            typing.List[typing.Any]: The list of items that would be on the page.
        """

        try:
            return self._page_cache[page_number]
        except KeyError:
            pass
        try:
            if inspect.isasyncgenfunction(self.data) or inspect.isasyncgen(self.data):
                v = await self.data.__anext__()
            elif inspect.isgeneratorfunction(self.data) or inspect.isgenerator(self.data):
                v = next(self.data)
            elif inspect.iscoroutinefunction(self.data):
                v = await self.data(page_number)
            elif inspect.isfunction(self.data):
                v = self.data(page_number)
            else:
                v = self.data[page_number * self.per_page: (page_number + 1) * self.per_page]
            self._page_cache[page_number] = v
        except (StopIteration, StopAsyncIteration):
            self.max_pages = page_number
            page_number -= 1
            self.current_page -= 1
        return self._page_cache[page_number]

    @staticmethod
    def default_list_formatter(m, d):
        return Embed(
            use_random_colour=True,
            description="\n".join(d),
        ).set_footer(
            f"Page {m.current_page + 1}/{m.max_pages}",
        )

    @staticmethod
    def default_ranked_list_formatter(m, d):
        return Embed(
            use_random_colour=True,
            description="\n".join([
                f"{i}. {o}"
                for i, o in enumerate(d, start=(m.current_page * m.per_page) + 1)
            ])
        ).set_footer(
            f"Page {m.current_page + 1}/{m.max_pages}",
        )
