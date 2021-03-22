config_file = """
token = "bot_token"  # The token for the bot
owners = []  # List of owner IDs - these people override all permission checks
dm_uncaught_errors = false  # Whether or not to DM the owners when unhandled errors are encountered
user_agent = ""  # A custom string to populate Bot.user_agent with
default_prefix = "!"  # The prefix for the bot's commands
support_guild_id = 0  # The ID for the support guild - used by `Bot.fetch_support_guild()`
bot_support_role_id = 0  # The ID used to determine whether or not the user is part of the bot's support team - used for `.checks.is_bot_support()` check
guild_settings_prefix_column = "prefix"  # Used if multiple bots connect to the same database and need to seperate their prefixes

# Event webhook information - some of the events (noted) will be sent to the specified url
[event_webhook]
    event_webhook_url = ""
    [event_webhook.events]  # If you use true then your `event_webhook_url` will be used. If it's a string it'll assume that's a different webhook
        guild_join = false
        guild_remove = false
        shard_connect = false
        shard_disconnect = false
        shard_ready = false
        bot_ready = false
        unhandled_error = false

# The intents that the bot should start with
[intents]
    guilds = true  # Guilds - Used for guild join/remove, channel create/delete/update, Bot.get_channel, Bot.guilds, Bot.get_guild.
    members = false  # Members (privileged intent) - Used for member join/remove/update, Member.roles, Member.nick, User.name, Bot.get_user, Guild.get_member etc.
    bans = true  # Bans - Used for member ban/unban.
    emojis = true  # Emojis - Used for guild emojis update, Bot.get_emoji, Guild.emojis.
    integrations = true  # Integrations - Used for guild integrations update.
    webhooks = true  # Webhooks - Used for guild webhooks update.
    invites = true  # Invites - Used for invite create/delete.
    voice_states = true  # Voice states - Used for voice state update, VoiceChannel.members, Member.voice.
    presences = false  # Presences (privileged intent) - Used for member update (for activities and status), Member.status.
    guild_messages = true  # Guild messages - Used for message events in guilds.
    dm_messages = true  # DM messages - Used for message events in DMs.
    guild_reactions = true  # Guild reactions - Used for [raw] reaction add/remove/clear events in guilds.
    dm_reactions = true  # DM reactions - Used for [raw] reaction add/remove/clear events in DMs.
    guild_typing = false  # Guild typing - Used for the typing event in guilds.
    dm_typing = false  # DM typing - Used for the typing event in Dms.

# Content to be included in the help command
[help_command]
    dm_help = true  # Whether or not the help embed should be DMd to the user
    content = ""  # Additional content to be sent with the embed

# Data used to send API requests to whatever service
[bot_listing_api_keys]
    topgg_token = ""  # The token used to post data to top.gg
    discordbotlist_token = ""  # The token used to post data to discordbotlist.com

# Data that's copied directly over to a command
[command_data]
    website_link = ""  # A link to be used on !website
    guild_invite = ""  # A link to be used on !support
    github_link = ""  # A link to be used on !git
    donate_link = ""  # A link to be used on !donate
    invite_command_permissions = []  # args here are passed directly to discord.Permissions. An empty list disables the invite command
    echo_command_enabled = true  # Whether or not the echo command is enabled
    stats_command_enabled = true  # Whether or not the stats command is enabled
    vote_command_enabled = false  # Whether or not the top.gg vote command is enabled
    updates_channel_id = 0  # The ID of the news channel for the bot
    info = ""  # The text passed out with the !info command

# This data is passed directly over to asyncpg.connect()
[database]
    enabled = false
    user = "database_username"
    password = "database_password"
    database = "database_name"
    host = "127.0.0.1"
    port = 5432

# This data is passed directly over to aioredis.connect()
[redis]
    enabled = false
    host = "127.0.0.1"
    port = 6379
    db = 0

# The data that gets shoves into custom context for the embed
[embed]
    enabled = false  # whether or not to embed messages by default
    content = ""  # default content to be added to the embed message
    colour = 0  # a specific colour for the embed - 0 means random
    [embed.author]
        enabled = false
        name = "{ctx.bot.user}"
        url = ""  # the url added to the author
    [[embed.footer]]  # an array of possible footers
        text = "Add the bot to your server! ({ctx.clean_prefix}invite)"  # text to appear in the footer
        amount = 1  # the amount of times this particular text is added to the pool

# What the bot is playing
[presence]
    activity_type = "watching"  # Should be one of 'playing', 'listening', 'watching', 'competing'
    text = "VoxelBotUtils"
    status = "online"  # Should be one of 'online', 'invisible', 'idle', 'dnd'
    include_shard_id = true  # Whether or not to append "(shard N)" to the presence; only present if there's more than 1 shard
    [presence.streaming]  # This is used to automatically set the bot's status to your Twitch stream when you go live
        twitch_usernames = []  # The username of your Twitch.tv channel
        twitch_client_id = ""  # Your client ID - https://dev.twitch.tv/console/apps
        twitch_client_secret = ""  # Your client secret

# Used to generate the invite link - if not set then will use the bot's ID, which is correct more often than not
[oauth]
    client_id = ""

# UpgradeChat API key data - https://upgrade.chat/developers
[upgrade_chat]
    client_id = ""
    client_secret = ""
    [upgrade_chat.roles]
        "Role Name" = 0  # (role id)

# Statsd analytics port using the aiodogstatsd package
[statsd]
    host = "127.0.0.1"
    port = 8125  # This is the DataDog default, 9125 is the general statsd default
    [statsd.constant_tags]
        service = ""  # Put your bot name here - leave blank to disable stats collection
"""
