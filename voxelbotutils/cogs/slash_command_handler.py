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
        discord.TextChannel: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        discord.VoiceChannel: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        discord.CategoryChannel: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        discord.Role: utils.interactions.ApplicationCommandOptionType.ROLE,
        str: utils.interactions.ApplicationCommandOptionType.STRING,
        int: utils.interactions.ApplicationCommandOptionType.INTEGER,
        utils.converters.UserID: utils.interactions.ApplicationCommandOptionType.USER,
        utils.converters.ChannelID: utils.interactions.ApplicationCommandOptionType.CHANNEL,
        utils.converters.EnumConverter: utils.interactions.ApplicationCommandOptionType.STRING,
        utils.converters.BooleanConverter: utils.interactions.ApplicationCommandOptionType.BOOLEAN,
        utils.converters.ColourConverter: utils.interactions.ApplicationCommandOptionType.STRING,
        utils.converters.FilteredUser: utils.interactions.ApplicationCommandOptionType.USER,
        utils.converters.FilteredMember: utils.interactions.ApplicationCommandOptionType.USER,
        utils.TimeValue: utils.interactions.ApplicationCommandOptionType.STRING,
        inspect._empty: utils.interactions.ApplicationCommandOptionType.STRING,
    }

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.commands: typing.List[utils.interactions.ApplicationCommand] = None
        self.application_id = None

    async def get_context_from_interaction(self, payload, *, cls=utils.interactions.InteractionContext):
        # Make a context
        view = commands.view.StringView(f"<@{self.bot.user.id}> {payload['data']['name']} {' '.join([i['value'] for i in payload['data'].get('options', list())])}")
        fake_message = utils.interactions.InteractionMessage(
            guild=self.bot.get_guild(int(payload['guild_id'])),
            channel=self.bot.get_channel(int(payload['channel_id'])),
            author=self.bot.get_guild(int(payload['guild_id'])).get_member(int(payload['member']['user']['id'])),
            state=self.bot._get_state(),
            data=payload,
            content=view.buffer,
        )
        ctx = cls(prefix=f"<@{self.bot.user.id}> ", view=view, bot=self.bot, message=fake_message)
        ctx.is_slash_command = True
        ctx.original_author_id = int(payload['member']['user']['id'])
        view.skip_string(f"<@{self.bot.user.id}> ")
        invoker = view.get_word()

        # Make it work
        ctx.invoked_with = invoker
        ctx._interaction_webhook = discord.Webhook.partial(
            await self.bot.get_application_id(), payload["token"],
            adapter=discord.AsyncWebhookAdapter(self.bot.session)
        )
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
        return annotation.__args__[0]

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

    async def convert_into_application_command(self, ctx, command:typing.Union[utils.Command, utils.Group], *, is_option:bool=False) -> utils.interactions.ApplicationCommand:
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
            required = True
            if arg.annotation in self.COMMAND_TYPE_MAPPER:
                arg_type = arg.annotation
            elif self.is_typing_optional(arg.annotation) and self.get_non_optional_type(arg.annotation) in self.COMMAND_TYPE_MAPPER:
                arg_type = self.get_non_optional_type(arg.annotation)
                required = False
            if arg_type is None:
                raise Exception(f"Couldn't add a convert {command.qualified_name} into a slash command")
            safe_arg_type = self.COMMAND_TYPE_MAPPER[arg_type]
            if arg.default is not inspect._empty:
                required = False
            application_command.add_option(utils.interactions.ApplicationCommandOption(
                name=arg.name,
                description=f"The {arg.name} that you want to use for the {command.qualified_name} command.",
                type=safe_arg_type,
                required=required,
            ))

        # Go through its subcommands
        if isinstance(command, utils.Group):
            subcommands = list(command.walk_commands())
            valid_subcommands = [i for i in await self.bot.help_command.filter_commands_classmethod(ctx, subcommands) if getattr(i, 'add_slash_command', True)]
            for subcommand in valid_subcommands:
                application_command.add_option(await self.convert_into_application_command(ctx, subcommand, is_option=True))

        # Return command
        return application_command

    async def convert_all_into_application_command(self, ctx):
        slash_commands = []
        commands = list(ctx.bot.walk_commands())
        filtered_commands = [i for i in await self.bot.help_command.filter_commands_classmethod(ctx, commands) if getattr(i, 'add_slash_command', True)]
        for command in filtered_commands:
            slash_commands.append(await self.convert_into_application_command(ctx, command))
        return slash_commands

    @commands.command(cls=utils.Command)
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def addinteractioncommands(self, ctx, guild:bool):
        """
        Adds all of the bot's interaction commands to the global interaction handler.
        """

        # Get the commands we want to add
        ctx.author = ctx.guild.me
        application_command_list = await self.convert_all_into_application_command(ctx)
        current_commands = None

        # Get the commands that currently exist
        if guild:
            current_commands = await self.bot.get_guild_application_commands(ctx.guild)
        else:
            current_commands = await self.bot.get_global_application_commands()

        # See which commands we need to delete
        to_remove_commands = [i for i in current_commands if i.name not in [o.name for o in application_command_list]]
        for command in to_remove_commands:
            if guild:
                await self.bot.delete_guild_application_command(ctx.guild, command)
            else:
                await self.bot.delete_global_application_command(command)

        # Add the new commands
        async with ctx.typing():
            for command in application_command_list:
                try:
                    if guild:
                        await self.bot.add_guild_application_command(ctx.guild, command)
                    else:
                        await self.bot.add_global_application_command(command)
                except discord.HTTPException as e:
                    file_handle = io.StringIO(json.dumps(command.to_json(), indent=4))
                    file = discord.File(file_handle, filename="command.json")
                    await ctx.send(f"Failed to add `{command.name}` as a command - {e}", file=file)

        # And we done
        await ctx.okay()


def setup(bot):
    x = SlashCommandHandler(bot)
    bot.add_cog(x)
