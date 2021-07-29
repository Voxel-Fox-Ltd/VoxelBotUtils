import asyncio
import collections
import glob
import logging
import typing
import copy
from urllib.parse import urlencode
import string
import platform
import random
import json
import sys

import aiohttp
import toml
import discord
from discord.ext import commands
from discord.abc import Messageable
import upgradechat

from .custom_context import Context
from .database import DatabaseConnection
from .redis import RedisConnection
from .statsd import StatsdConnection
from .analytics_log_handler import AnalyticsLogHandler, AnalyticsClientSession
from .interactions.components import MessageComponents
from .models import ComponentMessage, ComponentWebhookMessage
from .shard_manager import ShardManagerClient
from . import interactions
from .. import all_packages as all_vfl_package_names


sys.path.append(".")


def get_prefix(bot, message: discord.Message):
    """
    Get the guild prefix for the bot given the message that should be invoking a command.
    """

    # Set our default
    config_prefix = bot.config.get('default_prefix')
    if not config_prefix and message.author.id not in bot.owner_ids:
        return " ".join(random.choices(string.whitespace, k=5))  # random string for a prefix if nothing is set

    # Default prefix for DMs
    if message.guild is None:
        prefix = config_prefix

    # Custom prefix or default prefix
    else:
        guild_prefix = bot.guild_settings[message.guild.id][bot.config.get('guild_settings_prefix_column', 'prefix')]
        prefix = guild_prefix or config_prefix

    # Fuck iOS devices
    if type(prefix) is not list and prefix in ["'", "‘"]:
        prefix = ["'", "‘"]

    # Listify it
    prefix = [prefix] if isinstance(prefix, str) else prefix
    prefix = [i for i in prefix if i]

    # Make it slightly more case insensitive
    prefix.extend([i.title() for i in prefix if i])
    prefix.extend([i.upper() for i in prefix if i])
    prefix.extend([i.lower() for i in prefix if i])
    prefix = list(set(prefix))  # Remove those duplicates

    # Add spaces for words
    possible_word_prefixes = [i for i in prefix if i and not any([o in i for o in string.punctuation])]
    prefix.extend([f"{i.strip()} " for i in possible_word_prefixes])

    # Add the bot's managed role
    if message.guild:
        try:
            managed_role = [i for i in message.guild.roles if i.tags and i.tags.bot_id == bot.user.id]
        except Exception:
            managed_role = None
        if managed_role:
            prefix.extend([f"<@&{managed_role[0].id}> "])

    # And we're FINALLY done
    return commands.when_mentioned_or(*prefix)(bot, message)


class RouteV8(discord.http.Route):
    BASE = 'https://discord.com/api/v8'


class MinimalBot(commands.AutoShardedBot):
    """
    A minimal version of the VoxelBotUtils bot that inherits from :class:`discord.ext.commands.AutoShardedBot`
    but gives new VBU features.
    """

    def __init__(self, *args, **kwargs):

        # Make sure we init the bot
        super().__init__(*args, **kwargs)

        # Add some attrs that appear in a lot of places
        self.application_id = None

        # Mess with the default D.py message send and edit methods
        async def send_button_msg_prop(messagable, *args, **kwargs) -> discord.Message:
            return await self._send_button_message(messagable, *args, **kwargs)

        async def add_reactions_prop(message, *reactions):
            for r in reactions:
                await message.add_reaction(r)

        async def edit_button_msg_prop(*args, **kwargs):
            return await self._edit_button_message(*args, **kwargs)

        async def wait_for_button_prop(*args, **kwargs):
            return await self._wait_for_button_message(*args, **kwargs)

        async def clear_components_msg_prop(message):
            return await message.edit(components=None)

        async def disable_components_msg_prop(message):
            return await message.edit(components=message.components.disable_components())

        async def enable_components_msg_prop(message):
            return await message.edit(components=message.components.enable_components())

        Messageable.send = send_button_msg_prop
        discord.message.MessageFlags.ephemeral = discord.flags.flag_value(lambda _: 64)
        discord.message.MessageFlags.VALID_FLAGS.update({"ephemeral": 64})

        discord.Message.add_reactions = add_reactions_prop

        discord.Message.edit = edit_button_msg_prop
        discord.Message.wait_for_button_click = wait_for_button_prop  # deprecated
        discord.Message.wait_for_component_interaction = wait_for_button_prop  # deprecated
        discord.Message.clear_components = clear_components_msg_prop
        discord.Message.disable_components = disable_components_msg_prop
        discord.Message.enable_components = enable_components_msg_prop

        discord.WebhookMessage.edit = edit_button_msg_prop
        discord.WebhookMessage.wait_for_button_click = wait_for_button_prop  # deprecated
        discord.WebhookMessage.wait_for_component_interaction = wait_for_button_prop  # deprecated
        discord.WebhookMessage.clear_components = clear_components_msg_prop
        discord.WebhookMessage.disable_components = disable_components_msg_prop
        discord.WebhookMessage.enable_components = enable_components_msg_prop

        discord.PartialMessage.edit = edit_button_msg_prop

    async def get_application_id(self) -> int:
        """
        Get the bot's application client ID.

        Returns:
            int: The bot's application ID.
        """

        if self.application_id:
            return self.application_id
        app = await self.application_info()
        self.application_id = app.id
        self._connection.application_id = app.id
        return self.application_id

    async def create_message_log(
            self, messages: typing.Union[typing.List[discord.Message], discord.iterators.HistoryIterator]) -> str:
        """
        Creates and returns an HTML log of all of the messages provided. This is an API method, and may
        raise an asyncio HTTP error.

        Args:
            messages (typing.Union[typing.List[discord.Message], discord.iterators.HistoryIterator]):
                The messages you want to create into a log.

        Returns:
            str: The HTML for a log file.
        """

        # Let's flatten the messages if we need to
        if isinstance(messages, discord.iterators.HistoryIterator):
            messages = await messages.flatten()

        # Create the data we're gonna send
        data = {
            "channel_name": messages[0].channel.name,
            "category_name": messages[0].channel.category.name,
            "guild_name": messages[0].guild.name,
            "guild_icon_url": str(messages[0].guild.icon_url),
        }
        data_authors = {}
        data_messages = []

        # Get the data from the server
        for message in messages:
            for user in message.mentions + [message.author]:
                data_authors[user.id] = {
                    "username": user.name,
                    "discriminator": user.discriminator,
                    "avatar_url": str(user.avatar_url),
                    "bot": user.bot,
                    "display_name": user.display_name,
                    "color": user.colour.value,
                }
            message_data = {
                "id": message.id,
                "content": message.content,
                "author_id": message.author.id,
                "timestamp": int(message.created_at.timestamp()),
                "attachments": [str(i.url) for i in message.attachments],
            }
            embeds = []
            for i in message.embeds:
                embed_data = i.to_dict()
                if i.timestamp:
                    embed_data.update({'timestamp': i.timestamp.timestamp()})
                embeds.append(embed_data)
            message_data.update({'embeds': embeds})
            data_messages.append(message_data)

        # Send data to the API
        data.update({"users": data_authors, "messages": data_messages[::-1]})
        async with self.session.post("https://voxelfox.co.uk/discord/chatlog", json=data) as r:
            return await r.text()

    async def create_global_application_command(self, command: interactions.ApplicationCommand) -> interactions.ApplicationCommand:
        """
        Add a global slash command for the bot.

        Args:
            command (voxelbotutils.ApplicationCommand): The command that you want to add.

        Returns:
            voxelbotutils.ApplicationCommand: The updated command instance using the returned API data.
        """

        application_id = await self.get_application_id()
        r = RouteV8(
            'POST', '/applications/{application_id}/commands',
            application_id=application_id,
        )
        data = await self.http.request(r, json=command.to_json())
        return interactions.ApplicationCommand.from_data(data)

    async def create_guild_application_command(
            self, guild: discord.Guild, command: interactions.ApplicationCommand) -> interactions.ApplicationCommand:
        """
        Add a guild-level slash command for the bot.

        Args:
            guild (discord.Guild): The guild you want to add the command to.
            command (voxelbotutils.ApplicationCommand): The command you want to add.

        Returns:
            voxelbotutils.ApplicationCommand: The updated command instance using the returned API data.
        """

        application_id = await self.get_application_id()
        r = RouteV8(
            'POST', '/applications/{application_id}/guilds/{guild_id}/commands',
            application_id=application_id, guild_id=guild.id,
        )
        data = await self.http.request(r, json=command.to_json())
        return interactions.ApplicationCommand.from_data(data)

    async def bulk_create_global_application_commands(
            self, commands: typing.List[interactions.ApplicationCommand]) -> typing.List[interactions.ApplicationCommand]:
        """
        Bulk add a global slash command for the bot.

        Args:
            commands (typing.List[voxelbotutils.ApplicationCommand]): The list of commands
                you want to add.

        Returns:
            typing.List[voxelbotutils.ApplicationCommand]: The updated command instances
                using the returned API data.
        """

        application_id = await self.get_application_id()
        r = RouteV8(
            'PUT', '/applications/{application_id}/commands',
            application_id=application_id,
        )
        data = await self.http.request(r, json=[i.to_json() for i in commands])
        return [interactions.ApplicationCommand.from_data(i) for i in data]

    async def bulk_create_guild_application_commands(
            self, guild: discord.Guild, commands: typing.List[interactions.ApplicationCommand]) -> typing.List[interactions.ApplicationCommand]:
        """
        Bulk add a guild-level slash command for the bot.

        Args:
            guild (discord.Guild): The guild you want to add the command to.
            commands (typing.List[voxelbotutils.ApplicationCommand]): The list of commands
                you want to add.

        Returns:
            typing.List[voxelbotutils.ApplicationCommand]: The updated command instances
                using the returned API data.
        """

        application_id = await self.get_application_id()
        r = RouteV8(
            'PUT', '/applications/{application_id}/guilds/{guild_id}/commands',
            application_id=application_id, guild_id=guild.id,
        )
        data = await self.http.request(r, json=[i.to_json() for i in commands])
        return [interactions.ApplicationCommand.from_data(i) for i in data]

    async def get_global_application_commands(self) -> typing.List[interactions.ApplicationCommand]:
        """
        Add a global slash command for the bot.

        Returns:
            typing.List[voxelbotutils.ApplicationCommand]: A list of commands that have been added.

        Returns:
            typing.List[voxelbotutils.ApplicationCommand]: The command instances
                that were previously added for the application.
        """

        application_id = await self.get_application_id()
        r = RouteV8(
            'GET', '/applications/{application_id}/commands',
            application_id=application_id,
        )
        data = await self.http.request(r)
        return [interactions.ApplicationCommand.from_data(i) for i in data]

    async def get_guild_application_commands(self, guild: discord.Guild) -> typing.List[interactions.ApplicationCommand]:
        """
        Add a guild-level slash command for the bot.

        Args:
            guild (discord.Guild): The guild you want to get commands for.

        Returns:
            typing.List[voxelbotutils.ApplicationCommand]: The command instances
                that were previously added for the application.
        """

        application_id = await self.get_application_id()
        r = RouteV8(
            'GET', '/applications/{application_id}/guilds/{guild_id}/commands',
            application_id=application_id, guild_id=guild.id,
        )
        data = await self.http.request(r)
        return [interactions.ApplicationCommand.from_data(i) for i in data]

    async def delete_global_application_command(self, command: interactions.ApplicationCommand) -> None:
        """
        Remove a global slash command for the bot.

        Args:
            command (voxelbotutils.ApplicationCommand): The command that you want to remove. A command
                ID is required for this to work.
        """

        application_id = await self.get_application_id()
        r = RouteV8(
            'DELETE', '/applications/{application_id}/commands/{command_id}',
            application_id=application_id, command_id=command.id,
        )
        return await self.http.request(r)

    async def delete_guild_application_command(
            self, guild: discord.Guild, command: interactions.ApplicationCommand) -> None:
        """
        Remove a guild-level slash command for the bot.

        Args:
            guild (discord.Guild): The guild that you want to remove the command on.
            command (interactions.ApplicationCommand): The command that you want to remove. A command
                ID is required for this to work.
        """

        application_id = await self.get_application_id()
        r = RouteV8(
            'DELETE', '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}',
            application_id=application_id, guild_id=guild.id, command_id=command.id,
        )
        return await self.http.request(r)

    async def get_context(self, message, *, cls=None) -> 'discord.ext.commands.Context':
        """
        Create a new context object using the utils' Context.

        :meta private:
        """

        return await super().get_context(message, cls=cls or Context)

    def get_context_message(self, channel, content, embed, *args, **kwargs):
        """
        A small base class for us to inherit from so that I don't need to change my
        send method when it's overridden.

        :meta private:
        """

        return content, embed

    async def _send_button_message(
            self, messageable, content: str = None, *, tts: bool = False,
            embed: discord.Embed = None, file: discord.File = None,
            files: typing.List[discord.File] = None, delete_after: float = None,
            nonce: str = None, allowed_mentions: discord.AllowedMentions = None,
            reference: discord.MessageReference = None, mention_author: bool = None,
            components: MessageComponents = None,
            ephemeral: bool = False, embeddify: bool = None,
            image_url: bool = None, embeddify_file: bool = True,
            wait: bool = True, embeds: typing.List[discord.Embed] = None,
            _no_wait_response_type: int = 4):
        """
        An alternative send method so that we can add components to messages.

        :meta private:
        """

        # Work out where we want to send to
        channel = await messageable._get_channel()
        content, embed = self.get_context_message(
            messageable, content=content, embed=embed, file=file, embeddify=embeddify,
            image_url=image_url, embeddify_file=embeddify_file,
        )
        try:
            state = messageable._state
        except AttributeError:
            state = self._connection
        lock = getattr(messageable, "_send_interaction_response_lock", asyncio.Lock())
        await lock.acquire()

        # Work out the main content
        content = str(content) if content is not None else None
        if embed is not None and embeds is not None:
            raise discord.InvalidArgument('cannot pass both embed and embeds parameter to send()')
        if embed is not None:
            embeds = [embed]
            embed = None
        if embeds and len(embeds) > 10:
            raise discord.InvalidArgument('embeds parameter must be a list of up to 10 elements')
        if embeds:
            embeds = [e.to_dict() for e in embeds]

        # Work out our allowed mentions
        if allowed_mentions is not None:
            if state.allowed_mentions is not None:
                allowed_mentions = state.allowed_mentions.merge(allowed_mentions).to_dict()
            else:
                allowed_mentions = allowed_mentions.to_dict()
        else:
            allowed_mentions = state.allowed_mentions and state.allowed_mentions.to_dict()

        # Work out our message references
        if mention_author is not None:
            allowed_mentions = allowed_mentions or discord.AllowedMentions().to_dict()
            allowed_mentions['replied_user'] = bool(mention_author)
        if reference is not None:
            try:
                reference = reference.to_message_reference_dict()
            except AttributeError:
                raise discord.InvalidArgument('reference parameter must be Message or MessageReference') from None

        # Make sure the files are valid
        if file is not None and files is not None:
            raise discord.InvalidArgument('cannot pass both file and files parameter to send()')
        if file:
            files = [file]
        if files and len(files) > 10:
            raise discord.InvalidArgument('files parameter must be a list of up to 10 elements')
        elif files and not all(isinstance(file, discord.File) for file in files):
            raise discord.InvalidArgument('files parameter must be a list of File')

        # Fix up the components
        if components:
            if not isinstance(components, MessageComponents):
                raise TypeError(f"Components kwarg must be of type {MessageComponents}")
            components = components.to_dict()

        # Send a response if it's an interaction
        if isinstance(channel, (list, tuple)):

            # Sent no responses but we want a message back - send a defer
            if not messageable._sent_ack_response and wait:
                await messageable.defer(ephemeral=ephemeral)

            # Sent no responses but we don't want a message object back from Discord
            elif not messageable._sent_ack_response:
                r = discord.http.Route('POST', '/interactions/{interaction_id}/{token}/callback', interaction_id=channel[0], token=channel[2])

            # A fallback for if someone says no wait but they HAVE sent an ack
            else:
                r = discord.http.Route('POST', '/webhooks/{app_id}/{token}', app_id=channel[1], token=channel[2])

            # Sent a defer that we should edit
            if wait and messageable.ACK_IS_EDITABLE and messageable._sent_ack_response and not messageable._sent_message_response:
                r = discord.http.Route('PATCH', '/webhooks/{app_id}/{token}/messages/@original', app_id=channel[1], token=channel[2])

            # Sent a defer and a response, or sent a defer with no editable original message
            elif wait:
                r = discord.http.Route('POST', '/webhooks/{app_id}/{token}', app_id=channel[1], token=channel[2])

        # Send a response if it's a channel
        else:
            r = discord.http.Route('POST', '/channels/{channel_id}/messages', channel_id=channel.id)

        # Build a payload to send
        payload = {}
        if content:
            payload['content'] = content
        if tts:
            payload['tts'] = True
        if embeds:
            payload['embeds'] = embeds
        if nonce:
            payload['nonce'] = nonce
        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions
        if reference:
            payload['message_reference'] = reference
        if components:
            payload['components'] = components
        if ephemeral:
            if not getattr(messageable, "CAN_SEND_EPHEMERAL", False):
                raise ValueError("Cannot send ephemeral messages with type {0.__class__}".format(messageable))
            payload['flags'] = discord.message.MessageFlags(ephemeral=True).value

        # Send the HTTP requests, including files
        if files is not None:
            form = []
            form.append({'name': 'payload_json', 'value': discord.utils.to_json(payload)})
            try:
                if len(files) == 1:
                    file = files[0]
                    form.append(
                        {
                            'name': 'file', 'value': file.fp,
                            'filename': file.filename, 'content_type': 'application/octet-stream',
                        }
                    )
                else:
                    for index, file in enumerate(files):
                        form.append(
                            {
                                'name': f'file{index}', 'value': file.fp,
                                'filename': file.filename, 'content_type': 'application/octet-stream',
                            }
                        )
                response_data = await messageable._state.http.request(r, form=form, files=files)
            finally:
                for f in files:
                    f.close()
        else:
            if isinstance(channel, (list, tuple)) and wait is False and messageable._sent_ack_response is False:
                payload = {"type": _no_wait_response_type, "data": payload.copy()}
            response_data = await messageable._state.http.request(r, json=payload)

        # Set the attributes for the interactions
        try:
            messageable._sent_ack_response = True
        except AttributeError:
            pass
        try:
            messageable._sent_message_response = True
        except AttributeError:
            pass

        # See if we want to respond with anything
        lock.release()
        if wait is False:
            return

        # Make the message object
        if isinstance(channel, (list, tuple)):
            webhook = discord.Webhook.partial(channel[1], channel[2], adapter=discord.AsyncWebhookAdapter(session=self.session))
            webhook._state = self._connection
            partial_webhook_state = discord.webhook._PartialWebhookState(webhook._adapter, webhook, parent=webhook._state)
            ret = ComponentWebhookMessage(data=response_data, state=partial_webhook_state, channel=messageable.channel)
        else:
            # ret = state.create_message(channel=channel, data=response_data)
            ret = ComponentMessage(state=state, channel=channel, data=response_data)

        # See if we want to delete the message
        if delete_after is not None:
            await ret.delete(delay=delete_after)

        # Return the created message
        return ret

    async def _edit_button_message(self, message, **fields):
        """
        An alternative message edit method so we can edit components onto messages.

        :meta private:
        """

        # Make the content
        try:
            content = fields['content']
        except KeyError:
            pass
        else:
            if content is not None:
                fields['content'] = str(content)

        # Make the embed[s]
        try:
            embed = fields.pop('embed')
        except KeyError:
            try:
                embeds = fields.pop('embeds')
            except KeyError:
                pass
            else:
                if embeds is not None:
                    embeds = [e.to_dict() for e in embeds]
                else:
                    embeds = []
                fields['embeds'] = embeds
        else:
            if embed is not None:
                embeds = [embed.to_dict()]
            else:
                embeds = []
            fields['embeds'] = embeds

        # Make the components
        try:
            components = fields['components']
        except KeyError:
            pass
        else:
            if components is not None:
                if not isinstance(components, MessageComponents):
                    raise TypeError(f"Components kwarg must be of type {MessageComponents}")
                fields['components'] = components.to_dict()
            else:
                fields['components'] = []

        # Make the supress flag
        try:
            suppress = fields.pop('suppress')
        except KeyError:
            pass
        else:
            flags = discord.message.MessageFlags._from_value(message.flags.value)
            flags.suppress_embeds = suppress
            fields['flags'] = flags.value

        # See if we should delete the message
        delete_after = fields.pop('delete_after', None)

        # Make the allowed mentions
        try:
            allowed_mentions = fields.pop('allowed_mentions')
        except KeyError:
            if message._state.allowed_mentions is not None:
                fields['allowed_mentions'] = message._state.allowed_mentions.to_dict()
        else:
            if allowed_mentions is not None:
                if message._state.allowed_mentions is not None:
                    allowed_mentions = message._state.allowed_mentions.merge(allowed_mentions).to_dict()
                else:
                    allowed_mentions = allowed_mentions.to_dict()
                fields['allowed_mentions'] = allowed_mentions

        # Make the attachments
        try:
            attachments = fields.pop('attachments')
        except KeyError:
            pass
        else:
            fields['attachments'] = [a.to_dict() for a in attachments]

        # Edit the message
        if fields:
            if isinstance(message, discord.WebhookMessage):
                r = discord.http.Route(
                    'PATCH', '/webhooks/{app_id}/{token}/messages/{message_id}',
                    app_id=message._state._webhook.id, token=message._state._webhook.token,
                    message_id=message.id,
                )
                response_data = await message._state.http.request(r, json=fields)
            else:
                response_data = await message._state.http.edit_message(message.channel.id, message.id, **fields)
            message._update(response_data)

        # See if we should delete the message
        if delete_after is not None:
            await message.delete(delay=delete_after)

    async def _wait_for_button_message(self, message, *, check=None, timeout=None):
        """
        Wait for an interaction on a button. Deprecated.

        :meta private:
        """

        message_check = lambda payload: payload.message.id == message.id
        if check:
            original_check = check
            check = lambda payload: original_check(payload) and message_check(payload)
        else:
            check = message_check
        return await self.wait_for("component_interaction", check=check, timeout=timeout)


class Bot(MinimalBot):
    """
    A bot class that inherits from :class:`voxelbotutils.MinimalBot`, detailing more VoxelBotUtils
    functions, as well as changing some of the default Discord.py library behaviour.

    Attributes:
        logger (logging.Logger): A logger instance for the bot.
        config (dict): The :class:`config<BotConfig>` for the bot.
        session (aiohttp.ClientSession): A session instance that you can use to make web requests.
        application_id (int): The ID of this bot application.
        database (DatabaseConnection): The database connector, as connected using the data
            from your :class:`config file<BotConfig.database>`.
        redis (RedisConnection): The redis connector, as connected using the data from your
            :class:`config file<BotConfig.redis>`.
        stats (StatsdConnection): The stats connector, as connected using the data from your
            :class:`config file<BotConfig.statsd>`. May not be authenticated, but will fail silently
            if not.
        startup_method (asyncio.Task): The task that's run when the bot is starting up.
        guild_settings (dict): A dictionary from the `guild_settings` Postgres table.
        user_settings (dict): A dictionary from the `user_settings` Postgres table.
        user_agent (str): The user agent that the bot should use for web requests as set in the
            :attr:`config file<BotConfig.user_agent>`. This isn't used automatically anywhere,
            so it just here as a provided convenience.
        upgrade_chat (upgradechat.UpgradeChat): An UpgradeChat connector instance using the oauth information
            provided in your :class:`config file<BotConfig.upgrade_chat>`.
        clean_prefix (str): The default prefix for the bot.
        owner_ids (typing.List[int]): A list of the owners from the :attr:`config file<BotConfig.owners>`.
        embeddify (bool): Whether or not messages should be embedded by default, as set in the
            :attr:`config file<BotConfig.embed.enabled>`.
    """

    def __init__(
            self, config_file: str = 'config/config.toml', logger: logging.Logger = None,
            activity: discord.Activity = discord.Game(name="Reconnecting..."),
            status: discord.Status = discord.Status.dnd, case_insensitive: bool = True,
            intents: discord.Intents = None,
            allowed_mentions: discord.AllowedMentions = discord.AllowedMentions(everyone=False),
            *args, **kwargs):
        """
        Args:
            config_file (str, optional): The path to the :class:`config file<BotConfig>` for the bot.
            logger (logging.Logger, optional): The logger object that the bot should use.
            activity (discord.Activity, optional): The default activity of the bot.
            status (discord.Status, optional): The default status of the bot.
            case_insensitive (bool, optional): Whether or not commands are case insensitive.
            intents (discord.Intents, optional): The default intents for the bot. Unless subclassed, the
                intents to use will be read from your :class:`config file<BotConfig.intents>`.
            allowed_mentions (discord.AllowedMentions, optional): The default allowed mentions for the bot.
            *args: The default args that are sent to the :class:`discord.ext.commands.Bot` object.
            **kwargs: The default args that are sent to the :class:`discord.ext.commands.Bot` object.
        """

        # Store the config file for later
        self.config = None
        self.config_file = config_file
        self.logger = logger or logging.getLogger('bot')
        self.reload_config()

        # Let's work out our intents
        if not intents:
            if self.config.get('intents', {}):
                intents = discord.Intents(**self.config.get('intents', {}))
            else:
                intents = discord.Intents(guilds=True, guild_messages=True, dm_messages=True)

        # Get our max messages
        cached_messages = self.config.get('cached_messages', 1_000)

        # Run original
        super().__init__(
            command_prefix=get_prefix, activity=activity, status=status, case_insensitive=case_insensitive, intents=intents,
            allowed_mentions=allowed_mentions, max_messages=cached_messages, *args, **kwargs,
        )

        # Set up our default guild settings
        self.DEFAULT_GUILD_SETTINGS = {
            self.config.get('guild_settings_prefix_column', 'prefix'): self.config['default_prefix'],
        }
        self.DEFAULT_USER_SETTINGS = {
        }

        # Aiohttp session
        self.session: aiohttp.ClientSession = AnalyticsClientSession(self, loop=self.loop)

        # Allow database connections like this
        self.database: DatabaseConnection = DatabaseConnection

        # Allow redis connections like this
        self.redis: RedisConnection = RedisConnection

        # Allow Statsd connections like this
        self.stats: StatsdConnection = StatsdConnection
        self.stats.config = self.config.get('statsd', {})

        # Gently add an UpgradeChat wrapper here - added as a property method so we can create a new instance if
        # the config is reloaded
        self._upgrade_chat = None

        # Store the startup method so I can see if it completed successfully
        self.startup_method = None
        self.shard_manager = None

        # Regardless of whether we start statsd or not, I want to add the log handler
        handler = AnalyticsLogHandler(self)
        handler.setLevel(logging.DEBUG)
        logging.getLogger('discord.http').addHandler(handler)
        logging.getLogger('discord.webhook').addHandler(handler)

        # Here's the storage for cached stuff
        self.guild_settings = collections.defaultdict(lambda: copy.deepcopy(self.DEFAULT_GUILD_SETTINGS))
        self.user_settings = collections.defaultdict(lambda: copy.deepcopy(self.DEFAULT_USER_SETTINGS))

    async def startup(self):
        """
        Clears the custom caches for the bot (:attr:`guild_settings` and :attr:`user_settings`),
        re-reads the database tables for each of those items, and calls the
        :func:`voxelbotutils.Cog.cache_setup` method in each of the cogs again.
        """

        try:
            await self._startup()
        except Exception as e:
            self.logger.error(e, exc_info=True)
            exit(1)

    async def _startup(self):
        """
        Runs all of the actual db stuff.
        """

        # Remove caches
        self.logger.debug("Clearing caches")
        self.guild_settings.clear()
        self.user_settings.clear()

        # Get database connection
        db = await self.database.get_connection()

        # Get default guild settings
        default_guild_settings = await db("SELECT * FROM guild_settings WHERE guild_id=0")
        if not default_guild_settings:
            default_guild_settings = await db("INSERT INTO guild_settings (guild_id) VALUES (0) RETURNING *")
        for i, o in default_guild_settings[0].items():
            self.DEFAULT_GUILD_SETTINGS.setdefault(i, o)

        # Get guild settings
        data = await self._get_all_table_data(db, "guild_settings")
        for row in data:
            for key, value in row.items():
                self.guild_settings[row['guild_id']][key] = value

        # Get default user settings
        default_user_settings = await db("SELECT * FROM user_settings WHERE user_id=0")
        if not default_user_settings:
            default_user_settings = await db("INSERT INTO user_settings (user_id) VALUES (0) RETURNING *")
        for i, o in default_user_settings[0].items():
            self.DEFAULT_USER_SETTINGS.setdefault(i, o)

        # Get user settings
        data = await self._get_all_table_data(db, "user_settings")
        for row in data:
            for key, value in row.items():
                self.user_settings[row['user_id']][key] = value

        # Run the user-added startup methods
        async def fake_cache_setup_method(db):
            pass
        for cog_name, cog in self.cogs.items():
            await getattr(cog, "cache_setup", fake_cache_setup_method)(db)

        # Wait for the bot to cache users before continuing
        self.logger.debug("Waiting until ready before completing startup method.")
        await self.wait_until_ready()

        # Close database connection
        await db.disconnect()

    async def _run_sql_exit_on_error(self, db, sql, *args):
        """
        Get data from a table, and exit if we get an error.
        """

        try:
            return await db(sql, *args)
        except Exception as e:
            self.logger.critical(f"Error selecting from table - {e}")
            exit(1)

    async def _get_all_table_data(self, db, table_name):
        """
        Select all from a table given its name.
        """

        return await self._run_sql_exit_on_error(db, "SELECT * FROM {0}".format(table_name))

    async def _get_list_table_data(self, db, table_name, key):
        """
        Select all from a table given its name and a `key=key` check.
        """

        return await self._run_sql_exit_on_error(db, "SELECT * FROM {0} WHERE key=$1".format(table_name), key)

    async def fetch_support_guild(self) -> typing.Optional[discord.Guild]:
        """
        Get the support guild as set in the bot's :attr:`config file<BotConfig.support_guild_id>`.

        Returns:
            typing.Optional[discord.Guild]: The guild instance. Will be `None` if a guild ID has not been
                provided, or cannot be found.
        """

        try:
            assert self.config['support_guild_id']
            return self.get_guild(self.config['support_guild_id']) or await self.fetch_guild(self.config['support_guild_id'])
        except Exception:
            return None

    def get_invite_link(
            self, *, base: str = None, client_id: int = None, scope: str = None,
            response_type: str = None, redirect_uri: str = None,
            guild_id: int = None, permissions: discord.Permissions = None,
            enabled: bool = None) -> str:
        """
        Generate an invite link for the bot.

        Args:
            base (str, optional): The base URL that should be used for the invite command. For almost all
                cases, the default of `https://discord.com/oauth2/authorize` is probably fine.
            client_id (int, optional): The client ID that the invite command should use. Uses the passed
                argument, then :attr:`the config's<BotConfig.oauth.client_id>` set client ID, and then the bot's
                ID if nothing is found.
            scope (str, optional): The scope for the invite link.
            response_type (str, optional): The response type of the invite link.
            redirect_uri (str, optional): The redirect URI for the invite link.
            guild_id (int, optional): The guild ID that the invite link should default to.
            permissions (discord.Permissions, optional): A permissions object that should be used to make
                the permissions on the invite.

        Returns:
            str: The URL for the invite.
        """

        # Make sure our permissions is a valid object
        permissions_object = discord.Permissions()
        if permissions is None:
            permissions = self.config.get("oauth", dict()).get("permissions", list())
        if isinstance(permissions, (list, set, tuple)):
            for p in permissions:
                setattr(permissions_object, p, True)
            permissions = permissions_object

        # Make the params for the url
        data = {
            'client_id': client_id or self.config.get('oauth', {}).get('client_id', None) or self.user.id,
            'scope': scope or self.config.get('oauth', {}).get('scope', None) or 'bot',
            'permissions': permissions.value,
        }
        if redirect_uri:
            data['redirect_uri'] = redirect_uri
        if guild_id:
            data['guild_id'] = guild_id
        if response_type:
            data['response_type'] = response_type

        # Return url
        return f"{base or 'https://discord.com/oauth2/authorize'}?" + urlencode(data)

    @property
    def user_agent(self):
        """:meta private:"""

        if self.user is None:
            return self.config.get("user_agent", (
                f"DiscordBot (Discord.py discord bot https://github.com/Rapptz/discord.py) "
                f"Python/{platform.python_version()} aiohttp/{aiohttp.__version__}"
            ))
        return self.config.get("user_agent", (
            f"{self.user.name.replace(' ', '-')} (Discord.py discord bot https://github.com/Rapptz/discord.py) "
            f"Python/{platform.python_version()} aiohttp/{aiohttp.__version__}"
        ))

    @property
    def upgrade_chat(self) -> upgradechat.UpgradeChat:
        """:meta private:"""

        if self._upgrade_chat:
            return self._upgrade_chat
        self._upgrade_chat = upgradechat.UpgradeChat(
            self.config["upgrade_chat"]["client_id"],
            self.config["upgrade_chat"]["client_secret"],
        )
        return self._upgrade_chat

    async def get_user_topgg_vote(self, user_id: int) -> bool:
        """
        Returns whether or not the user has voted on Top.gg. If there's no Top.gg token
        provided in your :attr:`config file<BotConfig.bot_listing_api_keys.topgg_token>`
        then this will always return `False`. This method doesn't handle timeouts or
        errors in their API (such as outages); you are expected to handle them yourself.

        Args:
            user_id (int): The ID of the user you want to check.

        Returns:
            bool: Whether or not that user has registered a vote on Top.gg.
        """

        # Make sure there's a token provided
        topgg_token = self.config.get('bot_listing_api_keys', {}).get('topgg_token')
        if not topgg_token:
            return False

        # Try and see whether the user has voted
        url = "https://top.gg/api/bots/{bot.user.id}/check".format(bot=self)
        async with self.session.get(url, params={"userId": user_id}, headers={"Authorization": topgg_token}) as r:
            try:
                data = await r.json()
            except Exception:
                return False
            if r.status != 200:
                return False

        # Return
        return data.get("voted", False)

    def get_event_webhook(self, event_name: str) -> typing.Optional[discord.Webhook]:
        """
        Get a :class:`discord.Webhook` object based on the keys in the
        :class:`bot's config<BotSettings.event_webhooks>`.

        Args:
            event_name (str): The name of the event you want to get a webhook for.

        Returns:
            typing.Optional[discord.Webhook]: A webhook instance pointing to the URL as given.
        """

        # First we're gonna use the legacy way of event webhooking, which is to say: it's just in the config
        url = self.config.get("event_webhook_url")
        if url:
            try:
                self.logger.debug("Grabbed event webhook from config")
                w = discord.Webhook.from_url(url, adapter=discord.AsyncWebhookAdapter(self.session))
                w._state = self._connection
                return w
            except discord.InvalidArgument:
                self.logger.error("The webhook set in your config is not a valid Discord webhook")
                return None
        if url is not None:
            return None

        # Now we're gonna do with the new handler
        webhook_picker = self.config.get("event_webhook")
        if webhook_picker is None:
            return None

        # See if the event is enabled
        new_url = webhook_picker.get("events", dict()).get(event_name)
        if new_url in ["", None, False]:
            return None
        if isinstance(new_url, str):
            url = new_url
        else:
            url = webhook_picker.get("event_webhook_url", "")
        try:
            self.logger.debug(f"Grabbed event webhook for event {event_name} from config")
            w = discord.Webhook.from_url(url, adapter=discord.AsyncWebhookAdapter(self.session))
            w._state = self._connection
            return w
        except discord.InvalidArgument:
            self.logger.error(f"The webhook set in your config for the event {event_name} is not a valid Discord webhook")
            return None

    async def add_delete_reaction(
            self, message: discord.Message, valid_users: typing.List[discord.User] = None, *,
            delete: typing.List[discord.Message] = None, timeout: float = 60.0, wait: bool = False) -> None:
        """
        Adds a delete reaction to the given message.

        Args:
            message (discord.Message): The message you want to add a delete reaction to.
            valid_users (typing.List[discord.User], optional): The users who have permission to use the message's delete reaction.
            delete (typing.List[discord.Message], optional): The messages that should be deleted on clicking the delete reaction.
            timeout (float, optional): How long the delete reaction should persist for.
            wait (bool, optional): Whether or not to block (via async) until the delete reaction is pressed.

        Raises:
            discord.HTTPException: The bot was unable to add a delete reaction to the message.
        """

        # See if we want to make this as a task or not
        if wait is False:
            return self.loop.create_task(self.add_delete_reaction(
                message=message, valid_users=valid_users, delete=delete, timeout=timeout, wait=True,
            ))

        # See if we were given a list of authors
        # This is an explicit check for None rather than just a falsy value;
        # this way users can still provide an empty list for only manage_messages users to be
        # able to delete the message.
        if valid_users is None:
            valid_users = (message.author,)

        # Let's not add delete buttons to DMs
        if isinstance(message.channel, discord.DMChannel):
            return

        # Add reaction
        try:
            await message.add_reaction("\N{WASTEBASKET}")
        except discord.HTTPException as e:
            raise e  # Maybe return none here - I'm not sure yet.

        # Fix up arguments
        if not isinstance(valid_users, (list, tuple, set)):
            valid_users = (valid_users,)

        # Wait for response
        def check(r, u) -> bool:
            if r.message.id != message.id:
                return False
            if u.bot is True:
                return False
            if isinstance(u, discord.Member) is False:
                return False
            if getattr(u, 'roles', None) is None:
                return False
            if str(r.emoji) != "\N{WASTEBASKET}":
                return False
            if u.id in [user.id for user in valid_users] or u.permissions_in(message.channel).manage_messages:
                return True
            return False
        try:
            await self.wait_for("reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            try:
                return await message.remove_reaction("\N{WASTEBASKET}", self.user)
            except Exception:
                return

        # We got a response
        if delete is None:
            delete = (message,)

        # Try and bulk delete
        bulk = False
        if message.guild:
            permissions: discord.Permissions = message.channel.permissions_for(message.guild.me)
            bulk = permissions.manage_messages and permissions.read_message_history
        try:
            await message.channel.purge(check=lambda m: m.id in [i.id for i in delete], bulk=bulk)
        except Exception:
            return  # Ah well

    def set_footer_from_config(self, embed: discord.Embed) -> None:
        """
        Sets a footer on the given embed based on the items in the
        :attr:`bot's config<BotConfig.embed.footer>`.

        Args:
            embed (discord.Embed): The embed that you want to set a footer on.
        """

        pool = []
        for data in self.config.get('embed', dict()).get('footer', list()):
            safe_data = data.copy()
            amount = safe_data.pop('amount')
            if amount <= 0:
                continue
            text = safe_data.pop('text')
            text = text.format(ctx=self)
            safe_data['text'] = text
            for _ in range(amount):
                pool.append(safe_data.copy())
        if not pool:
            return
        try:
            avatar_url = self.user.avatar_url
        except AttributeError:
            avatar_url = embed.Empty
        embed.set_footer(**random.choice(pool), icon_url=avatar_url)

    @property
    def clean_prefix(self):
        v = self.config['default_prefix']
        if isinstance(v, str):
            return v
        return v[0]

    @property
    def owner_ids(self) -> list:
        return self.config['owners']

    @owner_ids.setter
    def owner_ids(self, value):
        pass

    @property
    def embeddify(self) -> bool:
        try:
            return self.config['embed']['enabled']
        except Exception:
            return False

    def get_extensions(self) -> typing.List[str]:
        """
        Gets a list of filenames of all the loadable cogs.

        Returns:
            typing.List[str]: A list of the extensions found in the cogs/ folder,
                as well as the cogs included with VoxelBotUtils.
        """

        ext = glob.glob('cogs/[!_]*.py')
        extensions = []
        extensions.extend([f'voxelbotutils.cogs.{i}' for i in all_vfl_package_names])
        extensions.extend([i.replace('\\', '.').replace('/', '.')[:-3] for i in ext])
        self.logger.debug("Getting all extensions: " + str(extensions))
        return extensions

    def load_all_extensions(self) -> None:
        """
        Loads all the given extensions from :func:`voxelbotutils.Bot.get_extensions`.
        """

        # Unload all the given extensions
        self.logger.info('Unloading extensions... ')
        for i in self.get_extensions():
            try:
                self.unload_extension(i)
            except Exception as e:
                self.logger.debug(f' * {i}... failed - {e!s}')
            else:
                self.logger.info(f' * {i}... success')

        # Now load em up again
        self.logger.info('Loading extensions... ')
        for i in self.get_extensions():
            try:
                self.load_extension(i)
            except Exception as e:
                self.logger.critical(f' * {i}... failed - {e!s}')
                raise e
            else:
                self.logger.info(f' * {i}... success')

    async def set_default_presence(self, shard_id: int = None) -> None:
        """
        Sets the default presence for the bot as appears in the :class:`config file<BotConfig.presence>`.

        Args:
            shard_id (int, optional): The shard to set the presence for.
        """

        # Update presence
        self.logger.info("Setting default bot presence")
        presence = self.config.get("presence", {})  # Get presence object
        activity_type_str = presence.get("activity_type", "online").lower()  # Get the activity type (str)
        status = getattr(discord.Status, presence.get("status", "online").lower(), discord.Status.online)  # Get the activity type
        include_shard_id = presence.get("include_shard_id", False)  # Whether or not to include shard IDs
        activity_type = getattr(discord.ActivityType, activity_type_str, discord.ActivityType.playing)  # The activity type to use

        # Update per shard
        for i in self.shard_ids or [0]:

            # Update the config text
            config_text = presence.get("text", "").format(bot=self).strip()
            if self.shard_count > 1 and include_shard_id:
                config_text = f"{config_text} (shard {i})".strip()
                if config_text == f"(shard {i})":
                    config_text = f"Shard {i}"

            # Make an activity object
            if config_text:
                activity = discord.Activity(name=config_text, type=activity_type)
            else:
                activity = None

            # Update the presence
            await self.change_presence(activity=activity, status=status, shard_id=i)

    def reload_config(self) -> None:
        """
        Re-reads the config file into cache.
        """

        self.logger.info("Reloading config")
        try:
            with open(self.config_file) as a:
                self.config = toml.load(a)
            self._event_webhook = None
        except Exception as e:
            self.logger.critical(f"Couldn't read config file - {e}")
            exit(1)

        # Reset cache items that might need updating
        self._upgrade_chat = None

    async def login(self, token: str = None, *args, **kwargs):
        """:meta private:"""

        try:
            await super().login(token or self.config['token'], *args, **kwargs)
        except discord.HTTPException as e:
            if str(e).startswith("429 Too Many Requests"):
                headers = {i: o for i, o in dict(e.response.headers).items() if "rate" in i.lower()}
                self.logger.critical(f"Cloudflare rate limit reached - {json.dumps(headers)}")
            raise

    async def start(self, token: str = None, *args, **kwargs):
        """:meta private:"""

        # Say we're starting
        self.logger.info(f"Starting bot with {self.shard_count} shards")

        # See if we should run the startup method
        if self.config.get('database', {}).get('enabled', False):
            self.logger.info("Running startup method")
            self.startup_method = self.loop.create_task(self.startup())
        else:
            self.logger.info("Not running bot startup method due to database being disabled")

        # Get the recommended shard count for this bot
        async with aiohttp.ClientSession() as session:
            async with session.get("https://discord.com/api/v9/gateway/bot", headers={"Authorization": f"Bot {self.config['token']}"}) as r:
                data = await r.json()
        recommended_shard_count = None
        try:
            recommended_shard_count = data['shards']
            self.logger.info(f"Recommended shard count for this bot: {recommended_shard_count}")
            self.logger.info(f"Max concurrency for this bot: {data['session_start_limit']['max_concurrency']}")
        except KeyError:
            self.logger.info("Recommended shard count for this bot could not be retrieved")
        else:
            if recommended_shard_count / 2 > self.shard_count:
                self.logger.warning((
                    f"The shard count for this bot ({self.shard_count}) is significantly "
                    f"lower than the recommended number {recommended_shard_count}"
                ))

        # And run the original
        self.logger.info("Running original D.py start method")
        await super().start(token or self.config['token'], *args, **kwargs)

    async def close(self, *args, **kwargs):
        """:meta private:"""

        self.logger.debug("Closing aiohttp ClientSession")
        await asyncio.wait_for(self.session.close(), timeout=None)
        self.logger.debug("Running original D.py logout method")
        await super().close(*args, **kwargs)

    async def on_ready(self):
        self.logger.info(f"Bot connected - {self.user} // {self.user.id}")
        self.logger.info("Setting activity to default")
        await self.set_default_presence()
        self.logger.info('Bot loaded.')

    async def invoke(self, ctx):
        """:meta private:"""

        if ctx.command is None:
            return await super().invoke(ctx)
        command_stats_name = ctx.command.qualified_name.replace(' ', '_')
        command_stats_tags = {"command_name": command_stats_name, "slash_command": ctx.is_interaction}
        async with self.stats() as stats:
            stats.increment("discord.bot.commands", tags=command_stats_tags)
        return await super().invoke(ctx)

    def get_context_message(
            self, messageable, content: str, *, embed: discord.Embed = None,
            file: discord.File = None, embeddify: bool = None,
            image_url: str = None, embeddify_file: bool = True,
            **kwargs) -> typing.Tuple[str, discord.Embed]:
        """
        Takes a set of messageable content and outputs a string/Embed tuple that can be pushed
        into a messageable object.
        """

        if embeddify is None and image_url is not None:
            embeddify = True
        if embeddify is None:
            embeddify = self.embeddify

        # See if we need to check channel permissions at all
        if embeddify is False or embed is not None:
            should_not_embed = True
        else:
            try:
                try:
                    messageable_channel = messageable.channel
                except AttributeError:
                    messageable_channel = messageable
                channel_permissions: discord.Permissions = messageable_channel.permissions_for(messageable.guild.me)
                missing_embed_permission = not discord.Permissions(embed_links=True).is_subset(channel_permissions)
            except AttributeError:
                missing_embed_permission = False
            should_not_embed = any([
                missing_embed_permission,
                embeddify is False,
                embed is not None,
            ])

        # Can't embed? Just send it normally
        if should_not_embed:
            return content, embed

        # No current embed, and we _want_ to embed it? Alright!
        embed = discord.Embed(
            description=content,
            colour=random.randint(1, 0xffffff) or self.config.get('embed', dict()).get('colour', 0),
        )
        self.set_footer_from_config(embed)

        # Set image
        if image_url is not None:
            embed.set_image(url=image_url)
        if file and file.filename and embeddify_file:
            file_is_image = any([
                file.filename.casefold().endswith('.png'),
                file.filename.casefold().endswith('.jpg'),
                file.filename.casefold().endswith('.jpeg'),
                file.filename.casefold().endswith('.gif'),
                file.filename.casefold().endswith('.webm')
            ])
            if file_is_image:
                embed.set_image(url=f'attachment://{file.filename}')

        # Reset content
        content = self.config.get('embed', dict()).get('content', '').format(ctx=self) or None

        # Set author
        author_data = self.config.get('embed', dict()).get('author')
        if author_data.get('enabled', False):
            name = author_data.get('name', '').format(ctx=self) or discord.Embed.Empty
            url = author_data.get('url', '').format(ctx=self) or discord.Embed.Empty
            author_data = {
                'name': name,
                'url': url,
                'icon_url': self.user.avatar_url,
            }
            embed.set_author(**author_data)

        # Return information
        return content, embed

    async def launch_shard(self, gateway, shard_id: int, *, initial: bool = False):
        """
        Ask the shard manager if we're allowed to launch.

        :meta private:
        """

        # See if the shard manager is enabled
        shard_manager_config = self.config.get('shard_manager', {})
        shard_manager_enabled = shard_manager_config.get('enabled', False)

        # It isn't so Dpy can just do its thang
        if not shard_manager_enabled:
            return await super().launch_shard(gateway, shard_id, initial=initial)

        # Get the host and port to connect to
        host = shard_manager_config.get('host', '127.0.0.1')
        port = shard_manager_config.get('port', 8888)

        # Connect using our shard manager
        shard_manager = await ShardManagerClient.open_connection(host, port)
        await shard_manager.ask_to_connect(shard_id)
        await super().launch_shard(gateway, shard_id, initial=initial)
        await shard_manager.done_connecting(shard_id)

    async def launch_shards(self):
        """
        Launch all of the shards using the shard manager.

        :meta private:
        """

        # If we don't have redis, let's just ignore the shard manager
        shard_manager_enabled = self.config.get('shard_manager', {}).get('enabled', False)
        if not shard_manager_enabled:
            return await super().launch_shards()

        # Get the gateway
        if self.shard_count is None:
            self.shard_count, gateway = await self.http.get_bot_gateway()
        else:
            gateway = await self.http.get_gateway()

        # Set the shard count
        self._connection.shard_count = self.shard_count

        # Set the shard IDs
        shard_ids = self.shard_ids or range(self.shard_count)
        self._connection.shard_ids = shard_ids

        # Connect each shard
        shard_launch_tasks = []
        for shard_id in shard_ids:
            initial = shard_id == shard_ids[0]
            shard_launch_tasks.append(self.loop.create_task(self.launch_shard(gateway, shard_id, initial=initial)))

        # Wait for them all to connect
        await asyncio.wait(shard_launch_tasks)

        # Set the shards launched flag to true
        self._connection.shards_launched.set()

    async def connect(self, *, reconnect=True):
        """
        A version of connect that uses the shard manager.

        :meta private:
        """

        self._reconnect = reconnect
        await self.launch_shards()

        shard_manager_config = self.config.get('shard_manager', {})
        shard_manager_enabled = shard_manager_config.get('enabled', True)
        host = shard_manager_config.get('host', '127.0.0.1')
        port = shard_manager_config.get('port', 8888)
        queue = self._AutoShardedClient__queue  # I'm sorry Danny

        # Make a shard manager instance if we need to
        async def get_shard_manager():
            if not shard_manager_enabled:
                return
            return await ShardManagerClient.open_connection(host, port)

        while not self.is_closed():
            item = await queue.get()
            if item.type == discord.shard.EventType.close:
                await self.close()
                if isinstance(item.error, discord.errors.ConnectionClosed):
                    if item.error.code != 1000:
                        raise item.error
                    if item.error.code == 4014:
                        raise discord.errors.PrivilegedIntentsRequired(item.shard.id) from None
                return
            elif item.type == discord.shard.EventType.identify:
                shard_manager = await get_shard_manager()
                if shard_manager_enabled:
                    await shard_manager.ask_to_connect(item.shard.id, priority=True)  # Let's assign reidentifies a higher priority
                await item.shard.reidentify(item.error)
                if shard_manager_enabled:
                    await shard_manager.done_connecting(item.shard.id)
            elif item.type == discord.shard.EventType.resume:
                await item.shard.reidentify(item.error)
            elif item.type == discord.shard.EventType.reconnect:
                await item.shard.reconnect()
            elif item.type == discord.shard.EventType.terminate:
                await self.close()
                raise item.error
            elif item.type == discord.shard.EventType.clean_close:
                return
