import io
import traceback
import typing

import aiohttp
import discord
from discord.ext import commands

from . import utils as vbu


class ErrorHandler(vbu.Cog):

    COMMAND_ERROR_RESPONSES = (
        (
            vbu.errors.MissingRequiredArgumentString,
            lambda ctx, error: f"You're missing `{error.param}`, which is required for this command - see `{ctx.clean_prefix}help {' '.join(ctx.command.qualified_name.split(' ')[:-1] + [ctx.invoked_with])}`."
        ),
        (
            commands.MissingRequiredArgument,
            lambda ctx, error: f"You're missing `{error.param.name}`, which is required for this command - see `{ctx.clean_prefix}help {' '.join(ctx.command.qualified_name.split(' ')[:-1] + [ctx.invoked_with])}`."
        ),
        (
            (commands.UnexpectedQuoteError, commands.InvalidEndOfQuotedStringError, commands.ExpectedClosingQuoteError),
            lambda ctx, error: "The quotes in your message have been done incorrectly."
        ),
        # (
        #     vbu.checks.cooldown.NoRaiseCommandOnCooldown,
        #     lambda ctx, error: None
        # ),
        (
            commands.CommandOnCooldown,
            lambda ctx, error: f"You can't use this command again for another {vbu.TimeValue(error.retry_after).clean_spaced}."
        ),
        (
            vbu.errors.BotNotReady,
            lambda ctx, error: "The bot isn't ready to start processing that command yet - please wait."
        ),
        (
            commands.NSFWChannelRequired,
            lambda ctx, error: f"You can only run this command in channels set as NSFW. {'You can set channels as NSFW in their channel settings.' if ctx.channel.permissions_for(ctx.author).manage_channels else ''}"
        ),
        # (
        #     vbu.errors.BotNotInGuild,
        #     lambda ctx, error: "The bot needs to be in the guild for you to run this command."
        # ),
        # (
        #     vbu.errors.IsSlashCommand,
        #     lambda ctx, error: "This command cannot be run as a slash command."
        # ),
        # (
        #     vbu.errors.IsNotSlashCommand,
        #     lambda ctx, error: "This command can only be run as a slash command."
        # ),
        (
            commands.DisabledCommand,
            lambda ctx, error: "This command has been disabled."
        ),
        (
            vbu.errors.NotBotSupport,
            lambda ctx, error: "You need to be part of the bot's support team to be able to run this command."
        ),
        (
            commands.MissingAnyRole,
            lambda ctx, error: f"You need to have one of the {', '.join(['`' + i + '`' for i in error.missing_roles])} roles to be able to run this command."
        ),
        (
            commands.BotMissingAnyRole,
            lambda ctx, error: f"I need to have one of the {', '.join(['`' + i + '`' for i in error.missing_roles])} roles for you to be able to run this command."
        ),
        (
            commands.MissingRole,
            lambda ctx, error: f"You need to have the `{error.missing_role}` role to be able to run this command."
        ),
        (
            commands.BotMissingRole,
            lambda ctx, error: f"I need to have the `{error.missing_role}` role for you to be able to run this command."
        ),
        (
            commands.MissingPermissions,
            lambda ctx, error: f"You need the `{error.missing_perms[0]}` permission to run this command."
        ),
        (
            commands.BotMissingPermissions,
            lambda ctx, error: f"I need the `{error.missing_perms[0]}` permission for me to be able to run this command."
        ),
        (
            commands.NoPrivateMessage,
            lambda ctx, error: "This command can't be run in DMs."
        ),
        (
            commands.PrivateMessageOnly,
            lambda ctx, error: "This command can only be run in DMs."
        ),
        (
            commands.NotOwner,
            lambda ctx, error: "You need to be registered as an owner to run this command."
        ),
        (
            commands.MessageNotFound,
            lambda ctx, error: f"I couldn't convert `{error.argument}` into a message."
        ),
        (
            commands.MemberNotFound,
            lambda ctx, error: f"I couldn't convert `{error.argument}` into a guild member."
        ),
        (
            commands.UserNotFound,
            lambda ctx, error: f"I couldn't convert `{error.argument}` into a user."
        ),
        (
            commands.ChannelNotFound,
            lambda ctx, error: f"I couldn't convert `{error.argument}` into a channel."
        ),
        (
            commands.ChannelNotReadable,
            lambda ctx, error: f"I can't read messages in <#{error.argument.id}>."
        ),
        (
            commands.BadColourArgument,
            lambda ctx, error: f"I couldn't convert `{error.argument}` into a colour."
        ),
        (
            commands.RoleNotFound,
            lambda ctx, error: f"I couldn't convert `{error.argument}` into a role."
        ),
        (
            commands.BadInviteArgument,
            lambda ctx, error: f"I couldn't convert `{error.argument}` into an invite."
        ),
        (
            (commands.EmojiNotFound, commands.PartialEmojiConversionFailure),
            lambda ctx, error: f"I couldn't convert `{error.argument}` into an emoji."
        ),
        (
            commands.BadBoolArgument,
            lambda ctx, error: f"I couldn't convert `{error.argument}` into a boolean."
        ),
        (
            commands.BadUnionArgument,
            lambda ctx, error: f"I couldn't convert your provided `{error.param.name}` into any type of {', '.join([i.__name__.lower() for i in error.converters])}."
        ),
        (
            commands.BadArgument,
            lambda ctx, error: str(error).format(ctx=ctx, error=error)
        ),
        (
            commands.CommandNotFound,  # This is only handled in slash commands
            lambda ctx, error: "I wasn't able to find that command to be able to run it."
        ),
        (
            commands.TooManyArguments,
            lambda ctx, error: f"You gave too many arguments to this command - see `{ctx.clean_prefix}help {' '.join(ctx.command.qualified_name.split(' ')[:-1] + [ctx.invoked_with])}`."
        ),
        (
            discord.NotFound,
            lambda ctx, error: str(error).format(ctx=ctx, error=error)
        ),
        (
            commands.CheckFailure,
            lambda ctx, error: str(error).format(ctx=ctx, error=error)
        ),
        (
            discord.Forbidden,
            lambda ctx, error: ("Discord is saying I'm unable to perform that action.", "Discord is saying I'm unable to perform that action - I probably don't have permission to talk in that channel.")
        ),
        (
            (discord.HTTPException, aiohttp.ClientOSError),
            lambda ctx, error: "Either I or Discord messed up running this command. Please try again later."
        ),

        # Disabled because they're base classes for the subclasses above
        # (commands.CommandError, lambda ctx, error: ""),
        # (commands.CheckFailure, lambda ctx, error: ""),
        # (commands.CheckAnyFailure, lambda ctx, error: ""),
        # (commands.CommandInvokeError, lambda ctx, error: ""),
        # (commands.UserInputError, lambda ctx, error: ""),
        # (commands.ConversionError, lambda ctx, error: ""),
        # (commands.ArgumentParsingError, lambda ctx, error: ""),

        # Disabled because I've literally never used this and don't know anyone who has
        # (commands.MaxConcurrencyReached, lambda ctx, error: ""),

        # Disabled because they all refer to extension and command loading
        # (commands.ExtensionError, lambda ctx, error: ""),
        # (commands.ExtensionAlreadyLoaded, lambda ctx, error: ""),
        # (commands.ExtensionNotLoaded, lambda ctx, error: ""),
        # (commands.NoEntryPointError, lambda ctx, error: ""),
        # (commands.ExtensionFailed, lambda ctx, error: ""),
        # (commands.ExtensionNotFound, lambda ctx, error: ""),
        # (commands.CommandRegistrationError, lambda ctx, error: ""),
    )

    async def send_to_ctx_or_author(self, ctx: vbu.Context, text: str, author_text: str = None) -> typing.Optional[discord.Message]:
        """
        Tries to send the given text to ctx, but failing that, tries to send it to the author
        instead. If it fails that too, it just stays silent.
        """

        kwargs = {
            "content": text,
            "allowed_mentions": discord.AllowedMentions.none()
        }
        if isinstance(ctx, commands.SlashContext) and self.bot.config.get("ephemeral_error_messages", True):
            kwargs.update({"ephemeral": True})
        try:
            return await ctx.send(**kwargs)
        except discord.Forbidden:
            kwargs["content"] = text or author_text
            try:
                return await ctx.author.send(**kwargs)
            except discord.Forbidden:
                pass
        except discord.NotFound:
            pass
        return None

    @vbu.Cog.listener()
    async def on_command_error(self, ctx: vbu.Context, error: commands.CommandError):
        """
        Global error handler for all the commands around wew.
        """

        # Set up some errors that are just straight up ignored
        ignored_errors = (
            commands.CommandNotFound, vbu.errors.InvokedMetaCommand,
        )
        if isinstance(error, ignored_errors) and not isinstance(ctx, commands.SlashContext):
            return

        # See what we've got to deal with
        setattr(ctx, "original_author_id", getattr(ctx, "original_author_id", ctx.author.id))

        # Set up some errors that the owners are able to bypass
        owner_reinvoke_errors = (
            commands.MissingRole, commands.MissingAnyRole, commands.MissingPermissions,
            commands.CommandOnCooldown, commands.DisabledCommand, commands.CheckFailure,
            vbu.errors.IsNotUpgradeChatSubscriber, vbu.errors.IsNotVoter, vbu.errors.NotBotSupport,
        )
        if isinstance(error, owner_reinvoke_errors) and ctx.original_author_id in self.bot.owner_ids:
            if self.bot.config.get("owners_ignore_check_failures", True) and isinstance(error, commands.CheckFailure):
                pass
            else:
                return await ctx.reinvoke()

        # See if the command itself has an error handler AND it isn't a locally handlled arg
        # if hasattr(ctx.command, "on_error") and not isinstance(ctx.command, vbu.Command):
        if hasattr(ctx.command, "on_error"):
            return

        # See if it's in our list of common outputs
        output = None
        error_found = False
        for error_types, function in self.COMMAND_ERROR_RESPONSES:
            if isinstance(error, error_types):
                error_found = True
                output = function(ctx, error)
                break

        # See if they're tryina fuck me up
        if output is not None and ctx.message and output in ctx.message.content and isinstance(error, commands.NotOwner):
            output = "\N{UNAMUSED FACE}"

        # Send a message based on the output
        if output:
            try:
                _, _ = output
            except ValueError:
                output = (output,)
            return await self.send_to_ctx_or_author(ctx, *output)

        # Make sure not to send an error if it's "handled"
        if error_found:
            return

        # The output isn't a common output -- send them a plain error response
        try:
            await ctx.send(f"`{str(error).strip()}`", allowed_mentions=discord.AllowedMentions.none())
        except (discord.Forbidden, discord.NotFound):
            pass

        # Ping unhandled errors to the owners and to the event webhook
        error_string = "".join(traceback.format_exception(None, error, error.__traceback__))
        file_handle = io.StringIO(error_string + "\n")
        guild_id = ctx.guild.id if ctx.guild else None
        error_text = (
            f"Error `{error}` encountered.\nGuild `{guild_id}`, channel `{ctx.channel.id}`, "
            f"user `{ctx.author.id}`\n```\n{ctx.message.content if ctx.message else '[No message content]'}\n```"
        )

        # DM to owners
        if self.bot.config.get('dm_uncaught_errors', False):
            for owner_id in self.bot.owner_ids:
                owner = self.bot.get_user(owner_id) or await self.bot.fetch_user(owner_id)
                file_handle.seek(0)
                await owner.send(error_text, file=discord.File(file_handle, filename="error_log.py"))

        # Ping to the webook
        event_webhook: discord.Webhook = self.bot.get_event_webhook("unhandled_error")
        try:
            avatar_url = str(self.bot.user.display_avatar.url)
        except Exception:
            avatar_url = None
        if event_webhook:
            file_handle.seek(0)
            try:
                file = discord.File(file_handle, filename="error_log.py")
                await event_webhook.send(
                    error_text,
                    file=file,
                    username=f"{self.bot.user.name} - Error",
                    avatar_url=avatar_url,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            except discord.HTTPException as e:
                self.logger.error(f"Failed to send webhook for event unhandled_error - {e}")

        # And throw it into the console
        logger = getattr(getattr(ctx, 'cog', self), 'logger', self.logger)
        for line in error_string.strip().split("\n"):
            logger.error(line)


def setup(bot: vbu.Bot):
    x = ErrorHandler(bot)
    bot.add_cog(x)
