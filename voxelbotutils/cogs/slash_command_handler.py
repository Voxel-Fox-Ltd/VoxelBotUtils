import typing
import enum
import io
import json
import inspect

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
        str: utils.interactions.ApplicationCommandOptionType.STRING,
        int: utils.interactions.ApplicationCommandOptionType.INTEGER,
        inspect._empty: utils.interactions.ApplicationCommandOptionType.STRING,
    }

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.commands: typing.List[utils.interactions.ApplicationCommand] = None
        self.application_id = None

    async def get_context_from_interaction(self, payload, *, cls=utils.Context):
        """
        Make a context object from an interaction.
        """

        # Make a string view
        view = commands.view.StringView(
            f"<@{self.bot.user.id}> {payload['data']['name']} {' '.join([i['value'] for i in payload['data'].get('options', list())])}"
        )
        self.logger.debug(f"Made up fake string for interaction command: {view.buffer}")

        # Get some objects we can use to make the interaction message
        guild = self.bot.get_guild(int(payload['guild_id']))
        channel = self.bot.get_channel(int(payload['channel_id']))
        member_data = payload['member']
        member = discord.Member(data=member_data, guild=guild, state=self.bot._get_state())

        # Make our fake message
        fake_message = utils.interactions.InteractionMessage(
            guild=guild,
            channel=channel,
            author=member,
            state=self.bot._get_state(),
            data=payload,
            content=view.buffer,
        )
        ctx = cls(prefix=f"<@{self.bot.user.id}> ", view=view, bot=self.bot, message=fake_message)
        ctx.is_slash_command = True
        ctx.original_author_id = member.id
        view.skip_string(ctx.prefix)
        invoker = view.get_word()

        # Make it work
        ctx.invoked_with = invoker
        ctx._interaction_webhook = discord.Webhook.partial(
            await self.bot.get_application_id(), payload["token"],
            adapter=discord.AsyncWebhookAdapter(self.bot.session),
        )
        ctx._interaction_webhook._state = self.bot._get_state()
        ctx.command = self.bot.all_commands.get(invoker)

        # Send async data response
        self.logger.debug("Posting type 5 response for interaction command %s." % (str(payload)))
        url = "https://discord.com/api/v8/interactions/{id}/{token}/callback".format(id=payload["id"], token=payload["token"])
        await self.bot.session.post(url, json={"type": 5}, headers={"Authorization": f"Bot {self.bot.config['token']}"})

        # Return context
        return ctx

    @utils.Cog.listener()
    async def on_socket_response(self, payload):
        if payload['t'] != 'INTERACTION_CREATE':
            return
        self.logger.debug("Received interaction payload %s" % (str(payload)))
        ctx = await self.get_context_from_interaction(payload['d'])
        if ctx.command:
            self.logger.debug("Invoking interaction context for command %s" % (ctx.command.name))
        await self.bot.invoke(ctx)

    @staticmethod
    def is_typing_optional(annotation):
        """
        Stolen from Rapptz - https://github.com/Rapptz/discord.py/blob/60f804c63298d5f46a5ae4352b049d91b16d1b8c/discord/ext/commands/core.py#L975-L984
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
    def get_non_optional_type(annotation):
        try:
            return annotation.__args__[0]
        except Exception:
            return None

    async def get_slash_commands(self):
        """
        Get the application's global command objects.
        """

        if self.commands is not None:
            return self.commands
        url = "https://discord.com/api/applications/{application_id}/commands".format(application_id=await self.bot.get_application_id())
        headers = {"Authorization": f"Bot {self.bot.config['token']}"}
        site = await self.bot.session.get(url, headers=headers)
        data = await site.json()
        self.commands = [utils.interactions.ApplicationCommand.from_data(i) for i in data]
        return self.commands

    async def convert_into_application_command(
            self, ctx, command:typing.Union[utils.Command, utils.Group], *,
            is_option:bool=False) -> utils.interactions.ApplicationCommand:
        """
        Convert a given Discord command into an application command.
        """

        # Make command
        kwargs = {
            'name': command.name,
            'description': command.short_doc or f"Allows you to run the {command.qualified_name} command",
        }
        if is_option:
            application_command_type = utils.interactions.ApplicationCommandOptionType.SUBCOMMAND_GROUP if isinstance(command, utils.SubcommandGroup) else utils.interactions.ApplicationCommandOptionType.SUBCOMMAND
            kwargs.update({'type': application_command_type})
            application_command = utils.interactions.ApplicationCommandOption(**kwargs)
        else:
            application_command = utils.interactions.ApplicationCommand(**kwargs)

        # Go through its args
        for arg in command.clean_params.values():
            arg_type = None
            safe_arg_type = None
            required = True

            # See if it's one of our common types
            if arg.annotation in self.COMMAND_TYPE_MAPPER:
                safe_arg_type = self.COMMAND_TYPE_MAPPER[arg.annotation]
            elif self.get_non_optional_type(arg.annotation) in self.COMMAND_TYPE_MAPPER:
                safe_arg_type = self.COMMAND_TYPE_MAPPER[self.get_non_optional_type(arg.annotation)]

            # It isn't - let's see if it's a subclass
            if safe_arg_type is None:
                for i, o in self.COMMAND_TYPE_MAPPER.items():
                    if i in arg.annotation.mro()[1:]:
                        safe_arg_type = o
                        break

            # Make sure the type exists
            if safe_arg_type is None:
                raise Exception(f"Couldn't add a convert {command.qualified_name} into a slash command")

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
            valid_subcommands = [i for i in await self.bot.help_command.filter_commands_classmethod(ctx, subcommands) if getattr(i, 'add_slash_command', True)]
            for subcommand in valid_subcommands:
                application_command.add_option(await self.convert_into_application_command(ctx, subcommand, is_option=True))

        # Return command
        return application_command

    async def convert_all_into_application_command(self, ctx):
        slash_commands = []
        commands = list(ctx.bot.commands)
        filtered_commands = [i for i in await self.bot.help_command.filter_commands_classmethod(ctx, commands) if getattr(i, 'add_slash_command', True)]
        for command in filtered_commands:
            slash_commands.append(await self.convert_into_application_command(ctx, command))
        return slash_commands

    @commands.command(aliases=['addslashcommands'], cls=utils.Command)
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def addinteractioncommands(self, ctx, guild:bool):
        """
        Adds all of the bot's interaction commands to the global interaction handler.
        """

        # Get the commands we want to add
        ctx.author = ctx.guild.me
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

            # Loop through commands to add/update
            for command in commands_to_add:

                # See if we should bother updating it
                if command.to_json() in command_json_current:
                    self.logger.info(f"Didn't update slash command for {command.name}")
                    continue

                # Add command
                try:
                    if guild:
                        await self.bot.add_guild_application_command(ctx.guild, command)
                    else:
                        await self.bot.add_global_application_command(command)
                    self.logger.info(f"Added slash command for {command.name}")
                except discord.HTTPException as e:
                    file_handle = io.StringIO(json.dumps(command.to_json(), indent=4))
                    file = discord.File(file_handle, filename="command.json")
                    await ctx.send(f"Failed to add `{command.name}` as a command - {e}", file=file)

        # And we done
        await ctx.reply("Done.", embeddify=False)


def setup(bot):
    x = SlashCommandHandler(bot)
    bot.add_cog(x)
