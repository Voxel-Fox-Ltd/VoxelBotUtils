import collections

import discord
from discord.ext import commands


FakeResponse = collections.namedtuple("FakeResponse", ["status", "reason"])


class AbstractMentionable(discord.Object):
    """
    A fake mentionable object for use anywhere that you can't catch an error on a :code:`.mention` being None.

    Attributes:
        id (int): The ID of the mentionable.
        mention (str): The mention string for the object.
        name (str): The name of the object.
    """

    def __init__(self, id: int, mention: str = "null", name: str = "null"):
        """
        Args:
            id (int): The ID of the mentionable.
            mention (str): The string to be returned when :code:`.mention` is run.
            name (str): The string to be returned when :code:`.name` is run.
        """

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
        is_interaction (bool): Whether or not the context was invoked via an interaction
    """

    CAN_SEND_EPHEMERAL = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_author_id = self.author.id
        self.is_slash_command = False
        self.is_interaction = False
        self._send_interaction_response_task = None

    async def okay(self) -> None:
        """
        Adds the okay hand reaction to a message.
        """

        return await self.message.add_reaction("\N{OK HAND SIGN}")

    async def ack(self):
        """:meta private: Deprecated"""
        pass

    async def defer(self):
        """
        A defer method so we can use the same code for slash commands
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

    def get_mentionable_channel(self, channel_id: int, fallback: str = "null") -> AbstractMentionable:
        """
        Get the mention string for a given channel ID.

        Args:
            channel_id (int): The ID of the channel that you want to mention.
            fallback (str, optional): The string to fall back to if the channel isn't reachable.

        Returns:
            typing.Union[discord.TextChannel, voxelbotutils.AbstractMentionable]: The mentionable channel.
        """

        x = None
        if channel_id is not None:
            x = self.bot.get_channel(int(channel_id))
        if x:
            return x
        return AbstractMentionable(id, fallback, fallback)

    def get_mentionable_role(self, role_id: int, fallback: str = "null") -> AbstractMentionable:
        """
        Get the mention string for a given role ID.

        Args:
            role_id (int): The ID of the role that you want to mention.
            fallback (str, optional): The string to fall back to if the role isn't reachable.

        Returns:
            typing.Union[discord.Role, voxelbotutils.AbstractMentionable]: The mentionable role.
        """

        x = None
        if role_id is not None:
            x = self.guild.get_role(int(role_id))
        if x:
            return x
        return AbstractMentionable(id, fallback, fallback)
