import typing
import enum
import io
import json
import inspect
import asyncio

import discord
from discord.ext import commands

from . import utils


class SlashCommandHandler(utils.Cog):

    COMMAND_TYPE_MAPPER = {
        discord.User: utils.interactions.ApplicationCommandOptionType.USER,
        discord.Member: utils.interactions.ApplicationCommandOptionType.USER,
        commands.UserConverter: utils.interactions.ApplicationCommandOptionType.USER,
        commands.MemberConverter: utils.interactions.ApplicationCommandOptionType.USER,
        discord.TextChannel: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        commands.TextChannelConverter: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        discord.VoiceChannel: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        commands.VoiceChannelConverter: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        discord.CategoryChannel: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        commands.CategoryChannelConverter: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        discord.Role: utils.interactions.ApplicationCommandOptionType.ROLE,
        commands.RoleConverter: utils.interactions.ApplicationCommandOptionType.ROLE,
        utils.converters.UserID: utils.interactions.ApplicationCommandOptionType.USER,
        utils.converters.ChannelID: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        utils.converters.EnumConverter: utils.interactions.ApplicationCommandOptionType.STRING,
        utils.converters.BooleanConverter: utils.interactions.ApplicationCommandOptionType.BOOLEAN,
        utils.converters.ColourConverter: utils.interactions.ApplicationCommandOptionType.STRING,
        utils.converters.FilteredUser: utils.interactions.ApplicationCommandOptionType.USER,
        utils.converters.FilteredMember: utils.interactions.ApplicationCommandOptionType.USER,
        utils.TimeValue: utils.interactions.ApplicationCommandOptionType.STRING,
        commands.clean_content: utils.interactions.ApplicationCommandOptionType.STRING,
        str: utils.interactions.ApplicationCommandOptionType.STRING,
        int: utils.interactions.ApplicationCommandOptionType.INTEGER,
        inspect._empty: utils.interactions.ApplicationCommandOptionType.STRING,
    }

    def __init__(self, bot: utils.Bot):
        super().__init__(bot)
        self.commands: typing.List[utils.interactions.ApplicationCommand] = None
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
        return annotation.__args__[-1] is type(None)

    @staticmethod
    def is_typing_union(annotation) -> bool:
        try:
            if annotation.default is None:
                return True
        except AttributeError:
            pass
        try:
            origin = annotation.__origin__
            return True
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
            origin = annotation.__origin__
            return origin[0]
        except AttributeError:
            return None

    async def get_slash_commands(self) -> typing.List[utils.interactions.ApplicationCommand]:
        """
        Get the application's global command objects.
        """

        if self.commands is not None:
            return self.commands#
        r = discord.http.Route("GET", "/applications/{app_id}/commands", app_id=self.bot.application_id)
        data = await self.bot.http.request(r)
        self.commands = [utils.interactions.ApplicationCommand.from_data(i) for i in data]
        return self.commands

    async def convert_into_application_command(
            self, ctx, command: typing.Union[utils.Command, utils.Group], *,
            is_option: bool = False) -> utils.interactions.ApplicationCommand:
        """
        Convert a given Discord command into an application command.
        """

        # Make command
        kwargs = {
            'name': command.name,
            'description': command.short_doc or f"Allows you to run the {command.qualified_name} command",
        }
        if is_option:
            if isinstance(command, utils.SubcommandGroup):
                application_command_type = utils.interactions.ApplicationCommandOptionType.SUBCOMMAND_GROUP
            else:
                application_command_type = utils.interactions.ApplicationCommandOptionType.SUBCOMMAND
            kwargs.update({'type': application_command_type})
            application_command = utils.interactions.ApplicationCommandOption(**kwargs)
        else:
            application_command = utils.interactions.ApplicationCommand(**kwargs)

        # Go through its args
        for arg in command.clean_params.values():
            arg_type = None
            safe_arg_type = None
            required = True
            if self.is_typing_optional(arg.annotation):
                arg_type = self.get_non_optional_type(arg.annotation)
                required = False
            elif is_typing_union(arg.annotation):
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
                await ctx.send(f"Hit an error converting `{command.qualified_name}` command.")
                raise

            # Make sure the type exists
            if safe_arg_type is None:
                await ctx.send(f"Hit an error converting `{command.qualified_name}` command.")
                raise Exception(f"Couldn't convert {arg_type} into a valid slash command argument type.")

            # Say if it's optional
            if arg.default is not inspect._empty or self.is_typing_optional(arg.annotation):
                required = False

            # Add option
            application_command.add_option(utils.interactions.ApplicationCommandOption(
                name=arg.name,
                description=f"The {arg.name} that you want to use for the {command.qualified_name} command.",
                type=safe_arg_type,
                required=required,
            ))

        # Go through its subcommands
        if isinstance(command, utils.Group):
            subcommands = list(command.commands)
            valid_subcommands = []
            for i in (await self.bot.help_command.filter_commands_classmethod(ctx, subcommands)):
                if getattr(i, 'add_slash_command', True):
                    valid_subcommands.append(i)
            for subcommand in valid_subcommands:
                converted_option = await self.convert_into_application_command(ctx, subcommand, is_option=True)
                application_command.add_option(converted_option)

        # Return command
        return application_command

    async def convert_all_into_application_command(self, ctx: utils.Context) -> typing.List[utils.interactions.ApplicationCommand]:
        """
        Convert all of the commands for the bot into application commands.
        """

        slash_commands = []
        commands = list(ctx.bot.commands)
        filtered_commands = []
        for i in (await self.bot.help_command.filter_commands_classmethod(ctx, commands)):
            if getattr(i, 'add_slash_command', True):
                filtered_commands.append(i)
        for command in filtered_commands:
            slash_commands.append(await self.convert_into_application_command(ctx, command))
        return slash_commands

    @utils.command(aliases=['addslashcommands'])
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def addinteractioncommands(self, ctx, guild: bool = False, *, command_name: str = None):
        """
        Adds all of the bot's interaction commands to the global interaction handler.
        """

        # Get the commands we want to add
        ctx.author = ctx.guild.me
        if command_name:
            commands_to_add = [await self.convert_into_application_command(ctx, self.bot.get_command(command_name))]
        else:
            commands_to_add: typing.List[utils.interactions.ApplicationCommand] = await self.convert_all_into_application_command(ctx)
        command_names_to_add = [i.name for i in commands_to_add]

        # Start typing because this takes a while
        async with ctx.typing():

            # Get the commands that currently exist
            if guild:
                commands_current: typing.List[utils.interactions.ApplicationCommand] = await self.bot.get_guild_application_commands(ctx.guild)
            else:
                commands_current: typing.List[utils.interactions.ApplicationCommand] = await self.bot.get_global_application_commands()
            command_json_current = [i.to_json() for i in commands_current]

            # See which commands we need to delete
            commands_to_remove = [i for i in commands_current if i.name not in command_names_to_add]
            for command in commands_to_remove:
                if guild:
                    await self.bot.delete_guild_application_command(ctx.guild, command)
                else:
                    await self.bot.delete_global_application_command(command)
                self.logger.info(f"Removed slash command for {command.name}")

            # Add commands
            try:
                if guild:
                    await self.bot.bulk_create_guild_application_commands(ctx.guild, commands_to_add)
                else:
                    await self.bot.bulk_create_global_application_commands(commands_to_add)
            except discord.HTTPException as e:
                raise

        # And we done
        await ctx.reply("Done.", embeddify=False)

    @utils.command(aliases=['removeslashcommands'])
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def removeinteractioncommands(self, ctx, guild: bool, *, command_name: str = None):
        """
        Removes all of the bot's interaction commands from the global interaction handler.
        """

        # Get the commands we want to add
        ctx.author = ctx.guild.me
        if command_name:
            commands_to_add = [await self.convert_into_application_command(ctx, self.bot.get_command(command_name))]
        else:
            commands_to_add: typing.List[utils.interactions.ApplicationCommand] = await self.convert_all_into_application_command(ctx)
        command_names_to_add = [i.name for i in commands_to_add]

        # Start typing because this takes a while
        async with ctx.typing():

            # Get the commands that currently exist
            if guild:
                commands_current: typing.List[utils.interactions.ApplicationCommand] = await self.bot.get_guild_application_commands(ctx.guild)
            else:
                commands_current: typing.List[utils.interactions.ApplicationCommand] = await self.bot.get_global_application_commands()
            command_json_current = [i.to_json() for i in commands_current]

            # See which commands we need to delete
            for command in commands_current:
                if guild:
                    await self.bot.delete_guild_application_command(ctx.guild, command)
                else:
                    await self.bot.delete_global_application_command(command)
                self.logger.info(f"Removed slash command for {command.name}")

        # And we done
        await ctx.reply("Done.", embeddify=False)


def setup(bot: utils.Bot):
    x = SlashCommandHandler(bot)
    bot.add_cog(x)
