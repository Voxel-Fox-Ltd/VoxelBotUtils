import typing
import io
import json
import inspect

import discord
from discord.ext import commands

from . import utils as vbu


class ApplicationCommandHandler(vbu.Cog):

    COMMAND_TYPE_MAPPER = {
        discord.User: vbu.ApplicationCommandOptionType.USER,
        discord.Member: vbu.ApplicationCommandOptionType.USER,
        commands.UserConverter: vbu.ApplicationCommandOptionType.USER,
        commands.MemberConverter: vbu.ApplicationCommandOptionType.USER,
        discord.TextChannel: vbu.ApplicationCommandOptionType.CHANNEL,
        commands.TextChannelConverter: vbu.ApplicationCommandOptionType.CHANNEL,
        discord.VoiceChannel: vbu.ApplicationCommandOptionType.CHANNEL,
        commands.VoiceChannelConverter: vbu.ApplicationCommandOptionType.CHANNEL,
        discord.CategoryChannel: vbu.ApplicationCommandOptionType.CHANNEL,
        commands.CategoryChannelConverter: vbu.ApplicationCommandOptionType.CHANNEL,
        discord.Role: vbu.ApplicationCommandOptionType.ROLE,
        commands.RoleConverter: vbu.ApplicationCommandOptionType.ROLE,
        vbu.converters.UserID: vbu.ApplicationCommandOptionType.USER,
        vbu.converters.ChannelID: vbu.ApplicationCommandOptionType.CHANNEL,
        vbu.converters.EnumConverter: vbu.ApplicationCommandOptionType.STRING,
        vbu.converters.BooleanConverter: vbu.ApplicationCommandOptionType.BOOLEAN,
        vbu.converters.ColourConverter: vbu.ApplicationCommandOptionType.STRING,
        vbu.converters.FilteredUser: vbu.ApplicationCommandOptionType.USER,
        vbu.converters.FilteredMember: vbu.ApplicationCommandOptionType.USER,
        vbu.TimeValue: vbu.ApplicationCommandOptionType.STRING,
        commands.clean_content: vbu.ApplicationCommandOptionType.STRING,
        discord.Message: vbu.ApplicationCommandOptionType.STRING,
        discord.Emoji: vbu.ApplicationCommandOptionType.STRING,
        discord.PartialEmoji: vbu.ApplicationCommandOptionType.STRING,
        str: vbu.ApplicationCommandOptionType.STRING,
        int: vbu.ApplicationCommandOptionType.INTEGER,
        float: vbu.ApplicationCommandOptionType.NUMBER,
        inspect._empty: vbu.ApplicationCommandOptionType.STRING,
    }

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.commands: typing.List[vbu.ApplicationCommand] = None
        self.application_id = None

    @staticmethod
    def is_typing_optional(annotation) -> bool:
        """
        Returns whether or not the annotation is a `typing.Optional`.

        Stolen from Rapptz -
        discord.py/blob/60f804c63298d5f46a5ae4352b049d91b16d1b8c/discord/ext/commands/core.py#L975-L984
        """

        try:
            if annotation.default is None:
                return True
        except AttributeError:
            pass
        try:
            origin = annotation.__origin__
        except AttributeError:
            return False
        if origin is not typing.Union:
            return False
        if len(annotation.__args__) != 2:
            return False
        return annotation.__args__[-1] is type(None)  # noqa

    @staticmethod
    def is_typing_union(annotation) -> bool:
        try:
            if annotation.default is None:
                return True
        except AttributeError:
            pass
        try:
            return annotation.__origin__ is typing.Union
        except AttributeError:
            return False

    @staticmethod
    def get_non_optional_type(annotation) -> typing.Optional[typing.Any]:
        """
        Gets the optional type out of a `typing.Optional`.
        """

        try:
            return annotation.__args__[0]
        except Exception:
            return None

    @staticmethod
    def get_union_type(annotation) -> bool:
        try:
            if annotation.default is None:
                return True
        except AttributeError:
            pass
        try:
            origin = annotation.__args__
            return origin[0]
        except AttributeError:
            return None

    @staticmethod
    def filter_commands(commands: list) -> list:
        """
        Return a list of filtered commands.
        """

        # Make sure they're enabled and visible
        commands = [
            i for i in commands
            if i.hidden is False and i.enabled is True and i.name not in ["help", "channelhelp", "commands"] and getattr(i, "add_slash_command", True)
        ]

        # Filter out owner-only commands
        commands = [
            i for i in commands
            if not any(
                o for o in i.checks
                if not f"{o.__module__}.{o.__qualname__}".startswith("discord.ext.commands.core.is_owner.")
            )
        ]

        # And return
        return commands

    @staticmethod
    def get_command_description(command) -> str:
        return command.short_doc or f"Allows you to run the {command.qualified_name} command"

    def convert_into_slash_command(
            self, command: typing.Union[vbu.Command, vbu.Group], *,
            is_option: bool = False) -> vbu.ApplicationCommand:
        """
        Convert a given Discord command into an application command.
        """

        # Make command
        kwargs = {
            'name': command.name,
            'description': self.get_command_description(command),
            'type': vbu.ApplicationCommandType.CHAT_INPUT,
        }
        if is_option:
            if isinstance(command, vbu.SubcommandGroup):
                application_command_type = vbu.ApplicationCommandOptionType.SUBCOMMAND_GROUP
            else:
                application_command_type = vbu.ApplicationCommandOptionType.SUBCOMMAND
            kwargs.update({'type': application_command_type})
            application_command = vbu.ApplicationCommandOption(**kwargs)
        else:
            application_command = vbu.ApplicationCommand(**kwargs)

        # Go through its args
        for index, arg in enumerate(command.clean_params.values()):
            arg_type = None
            safe_arg_type = None
            required = True
            if self.is_typing_optional(arg.annotation):
                arg_type = self.get_non_optional_type(arg.annotation)
                required = False
            elif self.is_typing_union(arg.annotation):
                arg_type = self.get_union_type(arg.annotation)
            else:
                arg_type = arg.annotation

            try:

                # See if it's one of our common types
                if arg_type in self.COMMAND_TYPE_MAPPER:
                    safe_arg_type = self.COMMAND_TYPE_MAPPER[arg_type]

                # It isn't - let's see if it's a subclass
                if safe_arg_type is None:
                    for i, o in self.COMMAND_TYPE_MAPPER.items():
                        if i in arg_type.mro()[1:]:
                            safe_arg_type = o
                            break

                # It isn't - let's try and get an attr from the class
                if safe_arg_type is None:
                    safe_arg_type = getattr(arg_type, "SLASH_COMMAND_ARG_TYPE", None)

            except Exception:
                raise Exception(f"Hit an error converting `{command.qualified_name}` command.")

            # Make sure the type exists
            if safe_arg_type is None:
                raise Exception(f"Couldn't convert {arg_type} into a valid slash command argument type for command `{command.qualified_name}`.")

            # Say if it's optional
            if arg.default is not inspect._empty or self.is_typing_optional(arg.annotation):
                required = False

            # Get the description
            description = f"The {arg.name} that you want to use for the {command.qualified_name} command."
            try:
                description = command.argument_descriptions[index] or description
            except (AttributeError, IndexError):
                pass

            # Add option
            application_command.add_option(vbu.ApplicationCommandOption(
                name=arg.name,
                description=description,
                type=safe_arg_type,
                required=required,
            ))

        # Go through its subcommands
        if isinstance(command, vbu.Group):
            subcommands = list(command.commands)
            valid_subcommands = []
            for i in self.filter_commands(subcommands):
                if getattr(i, 'add_slash_command', True):
                    valid_subcommands.append(i)
            for subcommand in valid_subcommands:
                converted_option = self.convert_into_slash_command(subcommand, is_option=True)
                application_command.add_option(converted_option)

        # Return command
        return application_command

    def convert_into_context_command(
            self, command: typing.Union[vbu.Command, vbu.Group]) -> vbu.ApplicationCommand:
        """
        Convert a given Discord command into an application command.
        """

        kwargs = {
            "name": command.context_command_name or command.name,
            "description": "ContextCommand",
            "type": command.context_command_type,
        }
        application_command = vbu.ApplicationCommand(**kwargs)
        return application_command

    def convert_all_into_application_command(self, ctx: vbu.Context) -> typing.List[vbu.ApplicationCommand]:
        """
        Convert all of the commands for the bot into application commands.
        """

        application_commands = []
        commands = list(ctx.bot.commands)
        filtered_commands = self.filter_commands(commands)
        for command in filtered_commands:
            application_commands.append(self.convert_into_slash_command(command))
            if getattr(command, "context_command_type", None):
                application_commands.append(self.convert_into_context_command(command))
        return application_commands

    @vbu.command(aliases=['addslashcommands', 'addslashcommand', 'addapplicationcommand'], add_slash_command=False)
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def addapplicationcommands(self, ctx, guild_only: bool, *commands: str):
        """
        Adds all of the bot's interaction commands to the global interaction handler.
        """

        # Get the commands we want to add
        ctx.author = ctx.guild.me
        if commands:
            commands_to_add = [await self.convert_into_application_command(ctx, self.bot.get_command(i)) for i in commands]
        else:
            commands_to_add: typing.List[vbu.ApplicationCommand] = self.convert_all_into_application_command(ctx)
        command_names_to_add = [i.name for i in commands_to_add]

        # Start typing because this takes a while
        async with ctx.typing():

            # Remove old slash commands if we're adding all of them as new
            if commands:

                # Get the commands that currently exist
                if guild_only:
                    commands_current: typing.List[vbu.ApplicationCommand] = await self.bot.get_guild_application_commands(ctx.guild)
                else:
                    commands_current: typing.List[vbu.ApplicationCommand] = await self.bot.get_global_application_commands()

                # See which commands we need to delete
                commands_to_remove = [i for i in commands_current if i.name not in command_names_to_add and i.type == vbu.ApplicationCommandType]
                for command in commands_to_remove:
                    if guild_only:
                        await self.bot.delete_guild_application_command(ctx.guild, command)
                    else:
                        await self.bot.delete_global_application_command(command)
                    self.logger.info(f"Removed slash command for {command.name}")

            # Add commands
            try:
                if guild_only:
                    await self.bot.bulk_create_guild_application_commands(ctx.guild, commands_to_add)
                else:
                    await self.bot.bulk_create_global_application_commands(commands_to_add)
            except discord.HTTPException as e:
                try:
                    file = discord.File(
                        io.StringIO(json.dumps([i.to_json() for i in commands_to_add], indent=4)),
                        filename="slash_commands.json",
                    )
                    error_text = await e.response.json()
                    await ctx.send(f"```json\n{json.dumps(error_text, indent=4)}```", file=file)
                except discord.HTTPException:
                    pass
                return

        # And we done
        await ctx.reply("Done.", embeddify=False)

    @vbu.command(aliases=['removeslashcommands', 'removeslashcommand', 'removeapplicationcommand'], add_slash_command=False)
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def removeapplicationcommands(self, ctx, guild_only: bool, *commands: str):
        """
        Removes the bot's interaction commands from the global interaction handler.
        """

        # Start typing because this takes a while
        async with ctx.typing():

            # Get the commands that currently exist
            if guild_only:
                commands_current: typing.List[vbu.ApplicationCommand] = await self.bot.get_guild_application_commands(ctx.guild)
            else:
                commands_current: typing.List[vbu.ApplicationCommand] = await self.bot.get_global_application_commands()

            # See which commands we need to delete
            for command in commands_current:
                if commands and command.name not in commands:
                    continue
                if guild_only:
                    await self.bot.delete_guild_application_command(ctx.guild, command)
                else:
                    await self.bot.delete_global_application_command(command)
                self.logger.info(f"Removed slash command for {command.name}")

        # And we done
        await ctx.reply("Done.", embeddify=False, wait=False)


def setup(bot: vbu.Bot):
    x = ApplicationCommandHandler(bot)
    bot.add_cog(x)
