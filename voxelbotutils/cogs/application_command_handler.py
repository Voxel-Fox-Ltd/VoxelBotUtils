import typing
import io
import json
import inspect
import argparse

import discord
from discord.ext import commands

from . import utils


class ApplicationCommandHandler(utils.Cog):

    COMMAND_TYPE_MAPPER = {
        discord.User: utils.ApplicationCommandOptionType.USER,
        discord.Member: utils.ApplicationCommandOptionType.USER,
        commands.UserConverter: utils.ApplicationCommandOptionType.USER,
        commands.MemberConverter: utils.ApplicationCommandOptionType.USER,
        discord.TextChannel: utils.ApplicationCommandOptionType.CHANNEL,
        commands.TextChannelConverter: utils.ApplicationCommandOptionType.CHANNEL,
        discord.VoiceChannel: utils.ApplicationCommandOptionType.CHANNEL,
        commands.VoiceChannelConverter: utils.ApplicationCommandOptionType.CHANNEL,
        discord.CategoryChannel: utils.ApplicationCommandOptionType.CHANNEL,
        commands.CategoryChannelConverter: utils.ApplicationCommandOptionType.CHANNEL,
        discord.Role: utils.ApplicationCommandOptionType.ROLE,
        commands.RoleConverter: utils.ApplicationCommandOptionType.ROLE,
        utils.converters.UserID: utils.ApplicationCommandOptionType.USER,
        utils.converters.ChannelID: utils.ApplicationCommandOptionType.CHANNEL,
        utils.converters.EnumConverter: utils.ApplicationCommandOptionType.STRING,
        utils.converters.BooleanConverter: utils.ApplicationCommandOptionType.BOOLEAN,
        utils.converters.ColourConverter: utils.ApplicationCommandOptionType.STRING,
        utils.converters.FilteredUser: utils.ApplicationCommandOptionType.USER,
        utils.converters.FilteredMember: utils.ApplicationCommandOptionType.USER,
        utils.TimeValue: utils.ApplicationCommandOptionType.STRING,
        commands.clean_content: utils.ApplicationCommandOptionType.STRING,
        discord.Message: utils.ApplicationCommandOptionType.STRING,
        discord.Emoji: utils.ApplicationCommandOptionType.STRING,
        discord.PartialEmoji: utils.ApplicationCommandOptionType.STRING,
        str: utils.ApplicationCommandOptionType.STRING,
        int: utils.ApplicationCommandOptionType.INTEGER,
        float: utils.ApplicationCommandOptionType.INTEGER,  # Controversial take
        inspect._empty: utils.ApplicationCommandOptionType.STRING,
    }

    def __init__(self, bot: utils.Bot):
        super().__init__(bot)
        self.commands: typing.List[utils.ApplicationCommand] = None
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

    async def get_slash_commands(self) -> typing.List[utils.ApplicationCommand]:
        """
        Get the application's global command objects.
        """

        if self.commands is not None:
            return self.commands
        r = discord.http.Route("GET", "/applications/{app_id}/commands", app_id=self.bot.application_id)
        data = await self.bot.http.request(r)
        self.commands = [utils.ApplicationCommand.from_data(i) for i in data]
        return self.commands

    @staticmethod
    def get_command_description(command) -> str:
        return command.short_doc or f"Allows you to run the {command.qualified_name} command"

    async def convert_into_application_command(
            self, ctx, command: typing.Union[utils.Command, utils.Group], *,
            is_option: bool = False) -> utils.ApplicationCommand:
        """
        Convert a given Discord command into an application command.
        """

        # Make command
        kwargs = {
            'name': command.name,
            'description': self.get_command_description(command),
            'type': utils.ApplicationCommandType.CHAT_INPUT,
        }
        if is_option:
            if isinstance(command, utils.SubcommandGroup):
                application_command_type = utils.ApplicationCommandOptionType.SUBCOMMAND_GROUP
            else:
                application_command_type = utils.ApplicationCommandOptionType.SUBCOMMAND
            kwargs.update({'type': application_command_type})
            application_command = utils.ApplicationCommandOption(**kwargs)
        else:
            application_command = utils.ApplicationCommand(**kwargs)

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
                await ctx.send(f"Hit an error converting `{command.qualified_name}` command.")
                raise

            # Make sure the type exists
            if safe_arg_type is None:
                await ctx.send(f"Hit an error converting `{command.qualified_name}` command.")
                raise Exception(f"Couldn't convert {arg_type} into a valid slash command argument type.")

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
            application_command.add_option(utils.ApplicationCommandOption(
                name=arg.name,
                description=description,
                type=safe_arg_type,
                required=required,
            ))

        # Go through its subcommands
        if isinstance(command, utils.Group):
            subcommands = list(command.commands)
            valid_subcommands = []
            for i in (await utils.HelpCommand.filter_commands_classmethod(ctx, subcommands)):
                if getattr(i, 'add_slash_command', True):
                    valid_subcommands.append(i)
            for subcommand in valid_subcommands:
                converted_option = await self.convert_into_application_command(ctx, subcommand, is_option=True)
                application_command.add_option(converted_option)

        # Return command
        return application_command

    async def convert_all_into_application_command(self, ctx: utils.Context) -> typing.List[utils.ApplicationCommand]:
        """
        Convert all of the commands for the bot into application commands.
        """

        slash_commands = []
        commands = list(ctx.bot.commands)
        filtered_commands = []
        for i in (await utils.HelpCommand.filter_commands_classmethod(ctx, commands)):
            if getattr(i, 'add_slash_command', True):
                filtered_commands.append(i)
        for command in filtered_commands:
            slash_commands.append(await self.convert_into_application_command(ctx, command))
        return slash_commands

    @utils.command(aliases=['addslashcommand'], argparse=(
        ("-commands", "-command", "-c", {"type": str, "nargs": "*"}),
        ("-delete-old", "-d", {"type": bool, "nargs": "?", "default": True}),
    ))
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def addslashcommands(self, ctx, guild_only: bool, *commands: str):
        """
        Adds all of the bot's interaction commands to the global interaction handler.
        """

        # Get the commands we want to add
        ctx.author = ctx.guild.me
        if commands:
            commands_to_add = [await self.convert_into_application_command(ctx, self.bot.get_command(i)) for i in commands]
        else:
            commands_to_add: typing.List[utils.ApplicationCommand] = await self.convert_all_into_application_command(ctx)
        command_names_to_add = [i.name for i in commands_to_add]

        # Start typing because this takes a while
        async with ctx.typing():

            # Remove old slash commands if we're adding all of them as new
            if commands:

                # Get the commands that currently exist
                if guild_only:
                    commands_current: typing.List[utils.ApplicationCommand] = await self.bot.get_guild_application_commands(ctx.guild)
                else:
                    commands_current: typing.List[utils.ApplicationCommand] = await self.bot.get_global_application_commands()

                # See which commands we need to delete
                commands_to_remove = [i for i in commands_current if i.name not in command_names_to_add and i.type == utils.ApplicationCommandType]
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

    @utils.command(aliases=['removeslashcommand'], argparse=(
        ("-commands", "-command", "-c", {"type": str, "nargs": "*"}),
    ))
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def removeslashcommands(self, ctx, guild_only: bool, *commands: str):
        """
        Removes the bot's interaction commands from the global interaction handler.
        """

        # Start typing because this takes a while
        async with ctx.typing():

            # Get the commands that currently exist
            if guild_only:
                commands_current: typing.List[utils.ApplicationCommand] = await self.bot.get_guild_application_commands(ctx.guild)
            else:
                commands_current: typing.List[utils.ApplicationCommand] = await self.bot.get_global_application_commands()

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

    @utils.command(aliases=['addcontextcommand'])
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def addcontextcommands(self, ctx, guild_only: bool, type_: str, *commands: str):
        """
        Add a list of context commands to a menu.
        """

        # Make sure the type is correct
        if type_.lower() not in ["user", "message"]:
            return await ctx.send("Your context command type needs to be one of **user** or **message**.")
        command_type = utils.ApplicationCommandType[type_.upper()]

        # Typing indicator
        async with ctx.typing():

            # Grab the commands
            commands_to_add = [self.bot.get_command(i) for i in commands]
            application_commands = [utils.ApplicationCommand(i.name, self.get_command_description(i), command_type) for i in commands_to_add]

            # And add them
            if guild_only:
                await self.bot.bulk_create_guild_application_commands(ctx.guild, application_commands)
            else:
                await self.bot.bulk_create_global_application_commands(application_commands)

        # And done
        await ctx.reply("Done.", embeddify=False, wait=False)


def setup(bot: utils.Bot):
    x = ApplicationCommandHandler(bot)
    bot.add_cog(x)
