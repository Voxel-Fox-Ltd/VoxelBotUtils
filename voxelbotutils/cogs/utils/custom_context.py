import typing
import asyncio
import random
import collections

import aiohttp
import discord
from discord.ext import commands


FakeResponse = collections.namedtuple("FakeResponse", ["status", "reason"])


class _FakeMentionable(discord.Object):

    def __init__(self, id: int, mention: str = "null", name: str = "null"):
        self.id = id
        self.mention = mention
        self.name = name

    def __str__(self):
        return self.name


class Context(commands.Context):
    """
    A modified version of the default :class:`discord.ext.commands.Context` to allow for things like
    slash commands and interaction responses, as well as implementing :func:`Context.clean_prefix`.

    Attributes:
        original_author_id (int): The ID of the original person to run the command. Persists through
            the bot's `sudo` command, if you want to check the original author.
        clean_prefix (str): A clean version of the prefix that the command was invoked with.
        IS_INTERACTION (bool): Whether or not the command was invoked via a slash command.
    """

    IS_INTERACTION = False
    CAN_SEND_EPHEMERAL = False

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

    async def ack(self):
        """
        An ack method so we can use the same code for slash commands
        as we do for text commands.
        """

        pass

    @property
    def clean_prefix(self) -> str:
        return self.prefix.replace(
            f"<@{self.bot.user.id}>",
            f"@{self.bot.user.name}",
        ).replace(
            f"<@!{self.bot.user.id}>",
            f"@{self.bot.user.name}",
        )

    def get_mentionable_channel(self, channel_id: int, fallback: str = "null") -> str:
        """
        Get the mention string for a given channel ID.

        Args:
            channel_id (int): The ID of the object that you want to mention.
            fallback (str, optional): The string to fall back to if the object isn't reachable.

        Returns:
            str: The mention string.
        """

        x = self.bot.get_channel(int(channel_id))
        if x:
            return x
        return _FakeMentionable(id, fallback, fallback)

    def get_mentionable_role(self, role_id: int, fallback: str = "null") -> str:
        """
        Get the mention string for a given role ID.

        Args:
            role_id (int): The ID of the object that you want to mention.
            fallback (str, optional): The string to fall back to if the object isn't reachable.

        Returns:
            str: The mention string.
        """

        x = self.guild.get_role(int(role_id))
        if x:
            return x
        return _FakeMentionable(id, fallback, fallback)
