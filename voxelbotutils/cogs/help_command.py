import random
import typing

import discord
from discord.ext import commands

from . import utils


class CustomHelpCommand(commands.MinimalHelpCommand):

    HELP_COMMAND_HIDDEN_ERRORS = (commands.DisabledCommand, commands.NotOwner, utils.errors.NotBotSupport, utils.errors.InvokedMetaCommand,)

    @classmethod
    async def filter_commands_classmethod(cls, ctx, commands_to_filter:typing.List[utils.Command]) -> typing.List[utils.Command]:
        """
        Filter the command list down into a list of runnable commands.
        """

        if ctx.author.id in ctx.bot.owner_ids:
            return [i for i in commands_to_filter if i.name != "help"]
        valid_commands = [i for i in commands_to_filter if i.hidden is False and i.enabled is True and i.name != "help"]
        returned_commands = []
        for comm in valid_commands:
            try:
                await comm.can_run(ctx)
            except commands.CommandError as e:
                if isinstance(e, cls.HELP_COMMAND_HIDDEN_ERRORS):
                    continue
            returned_commands.append(comm)
        return returned_commands

    async def filter_commands(self, commands_to_filter:typing.List[utils.Command]) -> typing.List[utils.Command]:
        """
        Filter the command list down into a list of runnable commands.
        """

        return await self.filter_commands_classmethod(self.context, commands_to_filter)

    def get_command_signature(self, command:commands.Command):
        return '{0.clean_prefix}{1.qualified_name} {1.signature}'.format(self, command)

    async def send_cog_help(self, cog:utils.Cog):
        """
        Sends help command for a cog.
        """

        return await self.send_bot_help({
            cog: cog.get_commands()
        })

    async def send_group_help(self, group:commands.Group):
        """
        Sends the help command for a given group.
        """

        return await self.send_bot_help({
            group: group.commands
        })

    async def send_command_help(self, command:utils.Command):
        """
        Sends the help command for a given command.
        """

        return await self.send_bot_help({
            command: []
        })

    async def send_bot_help(self, mapping:typing.Dict[typing.Optional[utils.Cog], typing.List[commands.Command]]):
        """
        Sends all help to the given channel.
        """

        # Get the visible commands for each of the cogs
        runnable_commands = {}
        for cog, cog_commands in mapping.items():
            available_commands = await self.filter_commands(cog_commands)
            if len(available_commands) > 0 or isinstance(cog, (commands.Command, commands.Group,)):
                runnable_commands[cog] = available_commands

        # Make an embed
        help_embed = self.get_initial_embed()

        # Add each command to the embed
        command_strings = []
        for cog, cog_commands in runnable_commands.items():
            value = '\n'.join([self.get_help_line(command) for command in cog_commands])
            try:
                cog_name = cog.qualified_name
            except AttributeError:
                cog_name = "Uncategorized"
            command_strings.append((cog_name, value))

            # See if it's a command with subcommands
            if isinstance(cog, commands.Group):
                help_embed.description = self.get_help_line(cog, with_signature=cog.invoke_without_command)
            if isinstance(cog, commands.Command):
                help_embed.description = self.get_help_line(cog, with_signature=True)

        # Order embed by length before embedding
        command_strings.sort(key=lambda x: len(x[1]), reverse=True)
        for name, value in command_strings:
            if value.strip():
                help_embed.add_field(
                    name=name,
                    value=value.strip(),
                )

        # Send it to the destination
        data = {"embed": help_embed}
        content = self.context.bot.config.get("help_command", {}).get("content", None)
        if content:
            data.update({"content": content.format(bot=self.context.bot, prefix=self.clean_prefix)})
        await self.send_to_destination(**data)

    async def send_to_destination(self, *args, **kwargs):
        """
        Sends content to the given destination.
        """

        dest = self.get_destination()

        # If the destination is a user
        if isinstance(dest, (discord.User, discord.Member, discord.DMChannel)):
            try:
                await dest.send(*args, **kwargs)
                if self.context.guild:
                    try:
                        await self.context.send("Sent you a DM!")
                    except discord.Forbidden:
                        pass  # Fail silently
            except discord.Forbidden:
                try:
                    await self.context.send("I couldn't send you a DM :c")
                except discord.Forbidden:
                    pass  # Oh no now they won't know anything
            except discord.HTTPException as e:
                await self.context.send(f"I couldn't send you the help DM - {e}")  # We couldn't send the embed for some other reason
            return

        # If the destination is a channel
        try:
            await dest.send(*args, **kwargs)
        except discord.Forbidden:
            pass  # Can't talk in the channel? Shame
        except discord.HTTPException as e:
            await self.context.send(f"I couldn't send you the help DM - {e}")  # We couldn't send the embed for some other reason

    async def send_error_message(self, error):
        """
        Sends an error message to the user.
        """

        try:
            await self.context.send(error)
        except discord.Forbidden:
            pass

    def get_initial_embed(self) -> discord.Embed:
        """
        Get the initial embed for that gets sent.
        """

        embed = discord.Embed()
        embed.set_author(name=self.context.bot.user, icon_url=self.context.bot.user.avatar_url)
        embed.colour = random.randint(1, 0xffffff)
        return embed

    def get_help_line(self, command:utils.Command, with_signature:bool=False):
        """
        Gets a doc line of help for a given command.
        """

        if command.short_doc:
            v = f"**{self.clean_prefix}{command.qualified_name}** - {command.short_doc}"
        else:
            v = f"**{self.clean_prefix}{command.qualified_name}**"
        if with_signature:
            v += f"\n`{self.clean_prefix}{command.qualified_name} {command.signature}`"
        return v

    def get_destination(self):
        """
        Return where we want the bot to send the embed to
        """

        if self.context.invoked_with.lower() == "channelhelp" and self.context.channel.permissions_for(self.context.author).manage_messages:
            return self.context.channel
        if self.context.bot.config.get("help_command", {}).get("dm_help", True):
            return self.context.author
        return self.context.channel


class Help(utils.Cog):

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelpCommand(dm_help=True)
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @utils.command(name="commands", hidden=True)
    async def _commands(self, ctx: utils.Context, *args):
        """
        An alias for help.
        """

        return await ctx.send_help(*args)

    @utils.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def channelhelp(self, ctx: utils.Context, *args):
        """
        An alias for help that outputs into the current channel.
        """

        return await ctx.send_help(*args)


def setup(bot:utils.Bot):
    x = Help(bot)
    bot.add_cog(x)
    bot.get_command("help")
