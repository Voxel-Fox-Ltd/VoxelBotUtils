import asyncio
import collections
import glob
import logging
import typing
import copy
from datetime import datetime as dt
from urllib.parse import urlencode
import string
import platform
import random

import aiohttp
import discord
import toml
from discord.ext import commands

from .custom_context import Context
from .database import DatabaseConnection
from .redis import RedisConnection
from .statsd import StatsdConnection
from .analytics_log_handler import AnalyticsLogHandler
from . import interactions
from .. import all_packages as all_vfl_package_names


def get_prefix(bot, message:discord.Message):
    """
    Gives the prefix for the bot - override this to make guild-specific prefixes.
    """

    # Default prefix for DMs
    if message.guild is None:
        prefix = bot.config['default_prefix']

    # Custom prefix or default prefix
    else:
        prefix = bot.guild_settings[message.guild.id][bot.config.get('guild_settings_prefix_column', 'prefix')] or bot.config['default_prefix']

    # Fuck iOS devices
    if type(prefix) is not list and prefix in ["'", "‘"]:
        prefix = ["'", "‘"]

    # Listify it
    prefix = [prefix] if isinstance(prefix, str) else prefix

    # Make it slightly more case insensitive
    prefix.extend([i.title() for i in prefix])

    # Add spaces for words
    possible_word_prefixes = [i for i in prefix if not any([o in i for o in string.punctuation])]
    prefix.extend([f"{i.strip()} " for i in possible_word_prefixes])

    # And we're FINALLY done
    return commands.when_mentioned_or(*prefix)(bot, message)


class RouteV8(discord.http.Route):
    BASE = 'https://discord.com/api/v8'


class Bot(commands.AutoShardedBot):
    """
    A child of discord.ext.commands.AutoShardedBot to make things a little easier when
    doing my own stuff.
    """

    def __init__(
            self, config_file:str='config/config.toml', logger:logging.Logger=None, activity:discord.Activity=discord.Game(name="Reconnecting..."),
            status:discord.Status=discord.Status.dnd, case_insensitive:bool=True, intents:discord.Intents=None,
            allowed_mentions:discord.AllowedMentions=discord.AllowedMentions(everyone=False), *args, **kwargs):
        """
        Args:
            config_file (str, optional): The path to the config file for the bot.
            logger (logging.Logger, optional): The logger object that the bot should use.
            activity (discord.Activity, optional): The default activity of the bot.
            status (discord.Status, optional): The default status of the bot.
            case_insensitive (bool, optional): Whether or not commands are case insensitive.
            intents (discord.Intents, optional): The default intents for the bot.
            allowed_mentions (discord.AllowedMentions, optional): The default allowed mentions for the bot.
            *args: The default args that are sent to the `discord.ext.commands.Bot` object.
            **kwargs: The default args that are sent to the `discord.ext.commands.Bot` object.
        """

        # Store the config file for later
        self.config = None
        self.config_file = config_file
        self.logger = logger or logging.getLogger('bot')
        self.reload_config()

        # Let's work out our intents
        if self.config.get('intents', {}):
            intents = discord.Intents(**self.config.get('intents', {}))
        else:
            intents = discord.Intents(guilds=True, guild_messages=True, dm_messages=True)

        # Run original
        super().__init__(
            command_prefix=get_prefix, activity=activity, status=status, case_insensitive=case_insensitive, intents=intents,
            allowed_mentions=allowed_mentions, *args, **kwargs,
        )

        # Set up our default guild settings
        self.DEFAULT_GUILD_SETTINGS = {
            self.config.get('guild_settings_prefix_column', 'prefix'): self.config['default_prefix'],
        }
        self.DEFAULT_USER_SETTINGS = {
        }

        # Aiohttp session
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(loop=self.loop)

        # Application ID (may not be bot ID)
        self._application_id = None

        # Allow database connections like this
        self.database: DatabaseConnection = DatabaseConnection
        self.database.logger = self.logger.getChild('database')

        # Allow redis connections like this
        self.redis: RedisConnection = RedisConnection
        self.redis.logger = self.logger.getChild('redis')

        # Allow Statsd connections like this
        self.stats: StatsdConnection = StatsdConnection
        self.stats.config = self.config.get('statsd', {})
        self.stats.logger = self.logger.getChild('statsd')

        # Store the startup method so I can see if it completed successfully
        self.startup_time = dt.now()
        self.startup_method = None

        # Regardless of whether we start statsd or not, I want to add the log handler
        handler = AnalyticsLogHandler(self)
        handler.setLevel(logging.DEBUG)
        logging.getLogger('discord.http').addHandler(handler)

        # Here's the storage for cached stuff
        self.guild_settings = collections.defaultdict(lambda: copy.deepcopy(self.DEFAULT_GUILD_SETTINGS))
        self.user_settings = collections.defaultdict(lambda: copy.deepcopy(self.DEFAULT_USER_SETTINGS))

    async def startup(self):
        """
        Clears all the bot's caches and fills them from a DB read
        """

        try:
            await self._startup()
        except Exception as e:
            self.logger.error(e)
            exit(1)

    async def _startup(self):
        """
        Runs the actual db stuff so I can wrap it in a try
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
        """Get data form a table, exiting if it can't"""

        try:
            return await db(sql, *args)
        except Exception as e:
            self.logger.critical(f"Error selecting from table - {e}")
            exit(1)

    async def _get_all_table_data(self, db, table_name):
        """Get all data from a table"""

        return await self._run_sql_exit_on_error(db, "SELECT * FROM {0}".format(table_name))

    async def _get_list_table_data(self, db, table_name, key):
        """Get all data from a table"""

        return await self._run_sql_exit_on_error(db, "SELECT * FROM {0} WHERE key=$1".format(table_name), key)

    async def fetch_support_guild(self) -> typing.Optional[discord.Guild]:
        """
        Fetch the support guild based on the config from the API.
        """

        return self.get_guild(self.config['support_guild_id']) or await self.fetch_guild(self.config['support_guild_id'])

    def get_invite_link(self, *, scope:str='bot', response_type:str=None, redirect_uri:str=None, guild_id:int=None, **kwargs) -> str:
        """
        Gets the invite link for the bot, with permissions all set properly.

        Args:
            scope (str, optional): The scope for the invite link.
            response_type (str, optional): The response type of the invite link.
            redirect_uri (str, optional): The redirect URI for the invite link.
            guild_id (int, optional): The guild ID that the invite link should default to.
            **kwargs: The permissions that should be attached to the invite link - passed directly to `discord.Permissions`.

        Returns:
            str: The URL for the invite.
        """

        # Make the permissions object
        permissions = discord.Permissions()
        for name, value in kwargs.items():
            setattr(permissions, name, value)

        # Make the params for the url
        data = {
            'client_id': self.config.get('oauth', {}).get('client_id', None) or self.user.id,
            'scope': scope,
            'permissions': permissions.value
        }
        if redirect_uri:
            data['redirect_uri'] = redirect_uri
        if guild_id:
            data['guild_id'] = guild_id
        if response_type:
            data['response_type'] = response_type

        # Return url
        return 'https://discord.com/oauth2/authorize?' + urlencode(data)

    @property
    def user_agent(self):
        return (
            f"{self.user.name.replace(' ', '-')} (Discord.py discord bot https://github.com/Rapptz/discord.py) "
            f"Python/{platform.python_version()} aiohttp/{aiohttp.__version__}"
        )

    def get_event_webhook(self, event_name:str) -> typing.Optional[discord.Webhook]:
        """
        Wowie it's time for webhooks
        """

        # First we're gonna use the legacy way of event webhooking, which is to say: it's just in the config
        url = self.config.get("event_webhook_url")
        if url:
            try:
                self.logger.debug("Grabbed event webhook from config")
                return discord.Webhook.from_url(url, adapter=discord.AsyncWebhookAdapter(self.session))
            except discord.InvalidArgument:
                self.logger.error("The webhook set in your config is not a valid Discord webhook")
                return None
        if url is not None:
            return

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
            return discord.Webhook.from_url(url, adapter=discord.AsyncWebhookAdapter(self.session))
        except discord.InvalidArgument:
            self.logger.error(f"The webhook set in your config for the event {event_name} is not a valid Discord webhook")
            return None

    async def get_application_id(self):
        if self._application_id:
            return self._application_id
        app = await self.application_info()
        self._application_id = app.id
        return self._application_id

    async def add_delete_button(self, message:discord.Message, valid_users:typing.List[discord.User]=None, *, delete:typing.List[discord.Message]=None, timeout=60.0, wait:bool=False) -> None:
        """
        Adds a delete button to the given message.

        Args:
            message (discord.Message): The message you want to add a delete button to.
            valid_users (typing.List[discord.User], optional): The users who have permission to use the message's delete button.
            delete (typing.List[discord.Message], optional): The messages that should be deleted on clicking the delete button.
            timeout (float, optional): How long the delete button should persist for.
            wait (bool, optional): Whether or not to block (via async) until the delete button is pressed.

        Raises:
            discord.HTTPException: The bot was unable to add a delete button to the message.
        """

        # See if we want to make this as a task or not
        if wait is False:
            self.loop.create_task(self.add_delete_button(message=message, valid_users=valid_users, delete=delete, timeout=timeout, wait=True))
            return

        # See if we were given a list of authors
        # This is an explicit check for None rather than just a falsy value;
        # this way users can still provide an empty list for only manage_messages users to be
        # able to delete the message.
        if valid_users is None:
            valid_users = [message.author]

        # Let's not add delete buttons to DMs
        if isinstance(message.channel, discord.DMChannel):
            return

        # Add reaction
        try:
            await message.add_reaction("\N{WASTEBASKET}")
        except discord.HTTPException as e:
            raise e  # Maybe return none here - I'm not sure yet.

        # Fix up arguments
        if not isinstance(valid_users, list):
            valid_users = [valid_users]

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
            delete = [message]

        # Try and bulk delete
        bulk = False
        if message.guild:
            permissions: discord.Permissions = message.channel.permissions_for(message.guild.me)
            bulk = permissions.manage_messages and permissions.read_message_history
        try:
            await message.channel.purge(check=lambda m: m.id in [i.id for i in delete], bulk=bulk)
        except Exception:
            return  # Ah well

    def set_footer_from_config(self, embed:discord.Embed) -> None:
        """
        Sets a footer on the embed from the config
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
        embed.set_footer(**random.choice(pool), icon_url=self.user.avatar_url)

    @property
    def clean_prefix(self):
        v = self.config.deafult_prefix
        if isinstance(v, str):
            return v
        return v[0]

    async def create_message_log(self, messages:typing.List[discord.Message]) -> str:
        """
        Args:
            messages (typing.List[discord.Message]): The messages you want to create into a log.

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
                # "embeds": [i.to_dict() for i in message.embeds],
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

    async def add_global_application_command(self, command:interactions.ApplicationCommand) -> None:
        """
        Add a global slash command for the bot.
        """

        application_id = await self.get_application_id()
        r = RouteV8('POST', '/applications/{application_id}/commands', application_id=application_id)
        return await self.http.request(r, json=command.to_json())

    async def add_guild_application_command(self, guild:discord.Guild, command:interactions.ApplicationCommand) -> None:
        """
        Add a guild-level slash command for the bot.
        """

        application_id = await self.get_application_id()
        r = RouteV8('POST', '/applications/{application_id}/guilds/{guild_id}/commands', application_id=application_id, guild_id=guild.id)
        return await self.http.request(r, json=command.to_json())

    async def get_global_application_commands(self) -> typing.List[interactions.ApplicationCommand]:
        """
        Add a global slash command for the bot.
        """

        application_id = await self.get_application_id()
        r = RouteV8('GET', '/applications/{application_id}/commands', application_id=application_id)
        data = await self.http.request(r)
        return [interactions.ApplicationCommand.from_data(i) for i in data]

    async def get_guild_application_commands(self, guild:discord.Guild) -> typing.List[interactions.ApplicationCommand]:
        """
        Add a guild-level slash command for the bot.
        """

        application_id = await self.get_application_id()
        r = RouteV8('GET', '/applications/{application_id}/guilds/{guild_id}/commands', application_id=application_id, guild_id=guild.id)
        data = await self.http.request(r)
        return [interactions.ApplicationCommand.from_data(i) for i in data]

    async def delete_global_application_command(self, command:interactions.ApplicationCommand) -> None:
        """
        Remove a global slash command for the bot.
        """

        application_id = await self.get_application_id()
        r = RouteV8('DELETE', '/applications/{application_id}/commands/{command_id}', application_id=application_id, command_id=command.id)
        return await self.http.request(r)

    async def delete_guild_application_command(self, guild:discord.Guild, command:interactions.ApplicationCommand) -> None:
        """
        Remove a guild-level slash command for the bot.
        """

        application_id = await self.get_application_id()
        r = RouteV8('DELETE', '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}', application_id=application_id, guild_id=guild.id, command_id=command.id)
        return await self.http.request(r)

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

    def get_uptime(self) -> float:
        """
        Gets the uptime of the bot in seconds.
        Uptime is a bit of a misnomer, since it starts when the instance is created, but yknow that's close enough.

        Returns:
            float: The total seconds that the bot's instance has been created for.
        """

        return (dt.now() - self.startup_time).total_seconds()

    async def get_context(self, message, *, cls=Context) -> 'discord.ext.commands.Context':
        """
        Create a new context object using the utils' Context.
        """

        return await super().get_context(message, cls=cls)

    def get_extensions(self) -> typing.List[str]:
        """
        Gets a list of filenames of all the loadable cogs.

        Returns:
            typing.List[str]: A list of the extensions found in the cogs/ folder, as well as the cogs included with the library.
        """

        ext = glob.glob('cogs/[!_]*.py')
        extensions = []
        extensions.extend([f'voxelbotutils.cogs.{i}' for i in all_vfl_package_names])
        extensions.extend([i.replace('\\', '.').replace('/', '.')[:-3] for i in ext])
        self.logger.debug("Getting all extensions: " + str(extensions))
        return extensions

    def load_all_extensions(self) -> None:
        """
        Loads all the given extensions from self.get_extensions().
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

    async def set_default_presence(self, shard_id:int=None) -> None:
        """
        Sets the default presence for the bot as appears in the config file.

        Args:
            shard_id (int, optional): The shard to set the presence for.
        """

        # Update presence
        self.logger.info("Setting default bot presence")
        presence = self.config["presence"]  # Get text

        # Update per shard
        if self.shard_count > 1 and presence.get("include_shard_id", True):

            # Go through each shard ID
            config_text = presence["text"].format(bot=self)
            for i in self.shard_ids:
                activity = discord.Activity(
                    name=f"{config_text} (shard {i})",
                    type=getattr(discord.ActivityType, presence['activity_type'].lower())
                )
                status = getattr(discord.Status, presence["status"].lower())
                await self.change_presence(activity=activity, status=status, shard_id=i)

        # Not sharded - just do everywhere
        else:
            activity = discord.Activity(
                name=presence["text"],
                type=getattr(discord.ActivityType, presence["activity_type"].lower())
            )
            status = getattr(discord.Status, presence["status"].lower())
            await self.change_presence(activity=activity, status=status)

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

    async def login(self, token:str=None, *args, **kwargs):
        await super().login(token or self.config['token'], *args, **kwargs)

    async def start(self, token:str=None, *args, **kwargs):
        if self.config.get('database', {}).get('enabled', False):
            self.logger.info("Running startup method")
            self.startup_method = self.loop.create_task(self.startup())
        else:
            self.logger.info("Not running bot startup method due to database being disabled")
        self.logger.info("Running original D.py start method")
        await super().start(token or self.config['token'], *args, **kwargs)

    async def close(self, *args, **kwargs):
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
        if ctx.command is None:
            return await super().invoke(ctx)
        command_stats_name = ctx.command.qualified_name.replace(' ', ':')
        command_stats_tags = {"command_name": command_stats_name}
        async with self.stats() as stats:
            stats.increment("discord.bot.commands", tags=command_stats_tags)
        return await super().invoke(ctx)
