import typing
import asyncio

import discord
from discord.ext import commands


class Paginator(object):
    """
    A helper class for paginating sets of data.
    """

    def __init__(
            self, data:typing.List[typing.Any], *, per_page:int=10,
            formatter:typing.Callable[['Paginator', typing.List[typing.Any]], dict]=None):
        """
        Args:
            data (typing.List[typing.Any]): The data that you want to paginate.
            per_page (int, optional): The number of items that appear on each page.
            formatter (typing.Callable[['Paginator', typing.List[typing.Any]], dict], optional): A function taking the
                paginator instance and a list of things to display, returning a dictionary of kwargs that get passed
                directly into a `Message.edit`.
        """
        self.data = data
        self.per_page = per_page
        self.formatter = formatter or (lambda paginator, data: {"content": "\n".join(str(i) for i in data)})
        self.current_page = None

        pages, left_over = divmod(len(data), self.per_page)
        if left_over:
            pages += 1
        self.max_pages = pages

    async def start(self, ctx:commands.Context, *, timeout:float=120):
        """
        Start and handle a paginator instance.

        Args:
            ctx (commands.Context): The context instance for the called command.
            timeout (float, optional): How long you should wait between getting a reaction and timing out.
        """

        # Set our initial values
        self.current_page = 0
        message = await ctx.send("Menu loading...")

        # Add the emojis if there's more than one page
        if self.max_pages > 1:
            valid_emojis = [
                "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}",
                "\N{LEFTWARDS BLACK ARROW}",
                "\N{BLACK RIGHTWARDS ARROW}",
                "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}",
            ]
            for e in valid_emojis:
                ctx.bot.loop.create_task(message.add_reaction(e))

        # Loop the reaction handler
        while True:

            # Edit the message with the relevant data
            items = self.get_page(self.current_page)
            payload = self.formatter(self, items)
            if isinstance(payload, discord.Embed):
                payload = {"embed": payload}
            elif isinstance(payload, str):
                payload = {"content": payload}
            payload.setdefault("content", None)
            payload.setdefault("embed", None)
            await message.edit(**payload)
            if self.max_pages == 1:
                return

            # Wait for reactions to be added by the user
            done, pending = None, None
            try:
                check = lambda p: str(p.emoji) in valid_emojis and p.user_id == ctx.author.id
                done, pending = await asyncio.wait([
                    ctx.bot.wait_for("raw_reaction_add", check=check),
                    ctx.bot.wait_for("raw_reaction_remove", check=check),
                ], return_when=asyncio.FIRST_COMPLETED, timeout=timeout)
            except asyncio.TimeoutError:
                pass

            # Remove the reactions if we're done
            if not done:
                try:
                    await message.clear_reactions()
                except discord.Exception:
                    pass
                return

            # See what they reacted with
            payload = done.pop().result()
            for future in pending:
                future.cancel()

            # Change the page number based on the reaction
            self.current_page = {
                "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}": lambda i: 0,
                "\N{LEFTWARDS BLACK ARROW}": lambda i: i - 1,
                "\N{BLACK RIGHTWARDS ARROW}": lambda i: i + 1,
                "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}": lambda i: self.max_pages,
            }[str(payload.emoji)](self.current_page)

            # Make sure the page number is still valid
            if self.current_page >= self.max_pages:
                self.current_page = self.max_pages - 1
            elif self.current_page < 0:
                self.current_page = 0

    def get_page(self, page_number:int) -> typing.List[typing.Any]:
        """
        Get a list of items that appear for a given page.

        Args:
            page_number (int): The page number to get.

        Returns:
            typing.List[typing.Any]: The list of items that would be on the page.
        """

        return self.data[page_number * self.per_page: (page_number + 1) * self.per_page]
