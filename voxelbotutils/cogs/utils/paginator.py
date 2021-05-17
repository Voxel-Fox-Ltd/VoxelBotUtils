import typing
import asyncio
import random
import inspect

import discord
from discord.ext import commands

from .context_embed import Embed


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
            # todo: rename?
            remove_reaction: bool = False
    ):
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
            remove_reaction (bool): Whether to remove the reaction when a reaction is added.
        """
        self.data = data
        self.per_page = per_page
        self.formatter = formatter
        if self.formatter is None:
            self.formatter = self.default_list_formatter
        self.remove_reaction = remove_reaction
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

        # Add the emojis if there's more than one page
        valid_emojis = [
            "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}",
            "\N{LEFTWARDS BLACK ARROW}",
            "\N{BLACK SQUARE FOR STOP}",
            "\N{BLACK RIGHTWARDS ARROW}",
        ]
        if self._data_is_iterable:
            valid_emojis.append("\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}")
            valid_emojis.append("\N{INPUT SYMBOL FOR NUMBERS}")
        add_emoji_tasks = []
        if self._data_is_iterable is False or self.max_pages > 1:
            add_emoji_tasks = [ctx.bot.loop.create_task(message.add_reaction(e)) for e in valid_emojis]

        # Loop the reaction handler
        last_payload = None
        while True:
            # Edit the message with the relevant data
            try:
                items = await self.get_page(self.current_page)
            except (KeyError, IndexError):
                await message.edit(content="There's no data to be shown.")
                break
            payload = self.formatter(self, items)
            if isinstance(payload, discord.Embed):
                payload = {"embed": payload}
            elif isinstance(payload, str):
                payload = {"content": payload}
            payload.setdefault("content", None)
            payload.setdefault("embed", None)
            if payload != last_payload:
                await message.edit(**payload)
            payload = last_payload
            if self.max_pages == 1:
                return

            # See if we now need to add a new emoji
            if self.max_pages != "?" and "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}" not in valid_emojis:
                ctx.bot.loop.create_task(message.add_reaction("\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}"))
                ctx.bot.loop.create_task(message.add_reaction("\N{INPUT SYMBOL FOR NUMBERS}"))
                valid_emojis.append("\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}")
                valid_emojis.append("\N{INPUT SYMBOL FOR NUMBERS}")

            # Wait for reactions to be added by the user
            done, pending = None, None
            try:
                check = lambda p: str(p.emoji) in valid_emojis and p.user_id == ctx.author.id and p.message_id == message.id
                done, pending = await asyncio.wait([
                    ctx.bot.wait_for("raw_reaction_add", check=check),
                    ctx.bot.wait_for("raw_reaction_remove", check=check),
                ], return_when=asyncio.FIRST_COMPLETED, timeout=timeout)
            except asyncio.TimeoutError:
                pass
            if not done:
                break

            # See what they reacted with
            payload = done.pop().result()
            for future in pending:
                future.cancel()

            # remove the reaction if applicable
            if self.remove_reaction and payload.event_type == "REACTION_ADD":
                try:
                    await ctx.message.remove_reaction(payload.emoji, ctx.author)
                except discord.Forbidden:
                    pass

            # Change the page number based on the reaction
            before_page = self.current_page
            self.current_page = {
                "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}": lambda i: 0,
                "\N{LEFTWARDS BLACK ARROW}": lambda i: i - 1,
                "\N{BLACK SQUARE FOR STOP}": lambda i: "STOP",
                "\N{BLACK RIGHTWARDS ARROW}": lambda i: i + 1,
                "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}": lambda i: self.max_pages,
                "\N{INPUT SYMBOL FOR NUMBERS}": lambda i: "CHANGE",
            }[str(payload.emoji)](self.current_page)
            if self.current_page == "STOP":
                break

            # Let the user ask for a page number
            if self.current_page == "CHANGE":
                ask_page_number_message = await ctx.send("What page do you want to change to?")
                try:
                    check = lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
                    change_page_number_message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
                except asyncio.TimeoutError:
                    break
                try:
                    self.current_page = int(change_page_number_message.content) - 1
                except ValueError:
                    self.current_page = before_page
                ctx.bot.loop.create_task(ask_page_number_message.delete())
                ctx.bot.loop.create_task(change_page_number_message.delete())

            # Make sure the page number is still valid
            if self.max_pages != "?" and self.current_page >= self.max_pages:
                self.current_page = self.max_pages - 1
            elif self.current_page < 0:
                self.current_page = 0

        # Let us break from the loop
        for t in add_emoji_tasks:
            t.cancel()
        ctx.bot.loop.create_task(message.clear_reactions())

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
