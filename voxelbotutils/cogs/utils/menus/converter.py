from __future__ import annotations

import asyncio
import typing

import discord
from discord.ext import commands

from .check import Check
from .errors import ConverterFailure, ConverterTimeout
from .utils import get_discord_converter

if typing.TYPE_CHECKING:
    AnyConverter = typing.Union[
        typing.Callable[[typing.Union[str, discord.Interaction[str]]], typing.Any],
        typing.Type[discord.Role],
        typing.Type[discord.TextChannel],
        typing.Type[discord.User],
        typing.Type[discord.Member],
        typing.Type[discord.VoiceChannel],
        typing.Type[str],
        typing.Type[int],
        typing.Type[bool],
    ]


class _FakeConverter(object):

    def __init__(self, callback):
        self.callback = callback

    async def convert(self, ctx, value):
        return self.callback(value)


class Converter(object):
    """
    An object for use in the settings menus for describing things that the user should input.
    """

    def __init__(
            self,
            prompt: str,
            checks: typing.List[Check] = None,
            converter: AnyConverter = str,
            components: discord.ui.MessageComponents = None,
            timeout_message: str = None):
        """
        Args:
            prompt (str): The message that should be sent to the user when asking for the convertable.
            checks (typing.List[voxelbotutils.menus.Check]): A list of check objects that should be used to make sure the user's
                input is valid. These will be silently ignored if a :code:`components` parameter is passed.
            converter (typing.Union[typing.Callable[[str], typing.Any], commands.Converter]): A callable that
                will be used to convert the user's input. If a converter fails then :code:`None` will be returned,
                so use the given checks to make sure that this does not happen if this behaviour is undesirable. If you set
                :code:`components`, then this function should instead take the payload instance that was given back by the
                user's interaction.
            components (voxelbotutils.MessageComponents): An instance of message components to be sent by the bot.
                If components are sent then the bot will not accept a message as a response, only an interaction
                with the component.
            timeout_message (str): The message that should get output to the user if this converter times out.
        """

        self.prompt = prompt
        self.checks = checks or list()
        self._converter = converter
        self.converter = self._wrap_converter(converter)
        self.components = components
        self.timeout_message = timeout_message

    @staticmethod
    def _wrap_converter(converter):
        """
        Wrap the converter so that it always has a `.convert` method.
        """

        converter = get_discord_converter(converter)
        if hasattr(converter, "convert"):
            try:
                return converter()
            except TypeError:
                return converter
        return _FakeConverter(converter)

    async def run(self, ctx: commands.Context, messages_to_delete: list = None):
        """
        Ask the user for an input, run the checks, run the converter, and return. Timeout errors
        *will* be raised here, but they'll propogate all the way back up to the main menu instance,
        which allows the bot to handle those much more gracefully instead of on a converter-by-converter
        basis.
        """

        # Ask the user for an input
        messages_to_delete = messages_to_delete if messages_to_delete is not None else list()
        sent_message = await ctx.send(self.prompt, components=self.components)
        messages_to_delete.append(sent_message)

        # The input will be an interaction - branch off here
        if self.components:
            def get_button_check(given_message):
                def button_check(payload):
                    if payload.message.id != given_message.id:
                        return False
                    if payload.user.id == ctx.author.id:
                        return True
                    ctx.bot.loop.create_task(payload.respond(f"Only {ctx.author.mention} can interact with these buttons.", ephemeral=True))
                    return False
                return button_check
            try:
                payload = await ctx.bot.wait_for("component_interaction", check=get_button_check(sent_message), timeout=60.0)
                await payload.response.defer_update()
            except asyncio.TimeoutError:
                raise ConverterTimeout(self.timeout_message)
            return await self.converter.convert(ctx, payload)

        # Loop until a valid input is received
        def check(message):
            return all([
                message.channel.id == ctx.channel.id,
                message.author.id == ctx.author.id,
            ])
        while True:

            # Wait for an input
            user_message = await ctx.bot.wait_for("message", check=check, timeout=60.0)
            messages_to_delete.append(user_message)

            # Run it through our checks
            checks_failed = False
            for c in self.checks:
                try:
                    checks_failed = not c.check(user_message)
                except Exception:
                    checks_failed = True
                if checks_failed:
                    break

            # Deal with a check failure
            if checks_failed:
                to_send_failure_message = c.fail_message
                if to_send_failure_message:
                    messages_to_delete.append(await ctx.send(to_send_failure_message))
                if c.on_failure == Check.failures.RETRY:
                    continue
                elif c.on_failure == Check.failures.FAIL:
                    raise ConverterFailure()
                return None  # We shouldn't reach here but this is just for good luck

            # And we converted properly
            return await self.converter.convert(ctx, user_message.content)
