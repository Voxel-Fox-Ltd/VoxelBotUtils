import typing
import asyncio
import random
import collections

import aiohttp
import discord
from discord.ext import commands


FakeResponse = collections.namedtuple("FakeResponse", ["status", "reason"])


class Context(commands.Context):

    DESIRED_PERMISSIONS = discord.Permissions(embed_links=True)

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

        return self.prefix.replace(f"<@{self.bot.user.id}>", f"@{self.bot.user.name}").replace(f"<@!{self.bot.user.id}>", f"@{self.bot.user.name}")

    # def _set_footer(self, embed:discord.Embed) -> None:
    #     """
    #     Sets a footer on the embed from the config
    #     """

    #     return self.bot.set_footer_from_config(embed)

    # async def _wait_until_interaction_sent(self):
    #     """
    #     Waits until the "_sent_interaction_response" attr is set to True before returning.
    #     """

    #     if self._send_interaction_response_task:
    #         while not self._send_interaction_response_task.done():
    #             await asyncio.sleep(0.1)
    #         result = self._send_interaction_response_task.result()
    #         if 200 <= result.status < 300:
    #             pass
    #         else:
    #             fr = FakeResponse(status=500, reason="Failed to create webhook.")
    #             raise discord.HTTPException(fr, fr.reason)
    #         self._send_interaction_response_task = None

    # async def send(
    #         self, content:str=None, *args, embed:discord.Embed=None, file:discord.File=None, embeddify:bool=None,
    #         embeddify_file:bool=True, image_url:str=None, **kwargs) -> typing.Optional[discord.Message]:
    #     """
    #     The normal `discord.abc.Messageable.send` but with an optional arg to ignore errors, as well as automatically
    #     embedding the content based on the bot's config.

    #     Args:
    #         content (str, optional): The content to be sent.
    #         *args: The default args for `discord.abc.Messageable.send`.
    #         embed (discord.Embed, optional): The embed object to be sent with the message.
    #         file (discord.File, optional): The file object to be sent with the message.
    #         embeddify (bool, optional): Whether or not to automatically embed the content of the message.
    #         embeddify_file (bool, optional): Whether or not ot automatically embed the file of the message.
    #         **kwargs: The default args for `discord.abc.Messageable.send`.

    #     Returns:
    #         discord.Message: The message that was returned to Discord.

    #     Raises:
    #         discord.HTTPException: If the message send should fail, this is the erorr that was raised.
    #     """

    #     content, embed = self.get_context_message(
    #         content=content, embed=embed, image_url=image_url, file=file, embeddify=embeddify,
    #         embeddify_file=embeddify_file,
    #     )
    #     try:
    #         location = getattr(self, '_interaction_webhook', super())
    #         if isinstance(location, discord.Webhook):
    #             kwargs['wait'] = True
    #         await self._wait_until_interaction_sent()
    #         return await location.send(content=content, *args, embed=embed, file=file, **kwargs)
    #     except Exception as e:
    #         if isinstance(e, aiohttp.ClientOSError):
    #             fr = FakeResponse(status=500, reason=str(e))
    #             raise discord.HTTPException(fr, fr.reason)
    #         raise e

    async def reply(self, *args, **kwargs):
        return await self.send(*args, reference=self.message, **kwargs)
