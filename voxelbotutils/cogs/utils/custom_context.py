import typing
import asyncio
import random
import collections

import aiohttp
import discord
from discord.ext import commands


FakeResponse = collections.namedtuple("FakeResponse", ["status", "reason"])


class Context(commands.Context):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_author_id = self.author.id
        self.is_slash_command = False
        self._send_interaction_response_task = None

    async def okay(self) -> None:
        """
        Adds the okay hand reaction to a message.
        """

        return await self.message.add_reaction("\N{OK HAND SIGN}")

    @property
    def clean_prefix(self):
        """
        Gives the prefix used to run the command but cleans up the bot mention.
        """

        return self.prefix.replace(
            f"<@{self.bot.user.id}>",
            f"@{self.bot.user.name}",
        ).replace(
            f"<@!{self.bot.user.id}>",
            f"@{self.bot.user.name}",
        )

    async def reply(self, *args, **kwargs):
        return await self.send(*args, reference=self.message, **kwargs)
