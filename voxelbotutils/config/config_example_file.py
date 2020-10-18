config_file = """
token = "bot_token"  # The token for the bot
owners = [ 141231597155385344, ]  # List of owner IDs - these people override all permission checks
dm_uncaught_errors = false  # Whether or not to DM the owners when unhandled errors are encountered
default_prefix = "!"  # The prefix for the bot's commands
event_webhook_url = ""  # Some events will be posted via webhook to this url

# The intents that the bot should start with
[intents]
    # Guilds - recommended: true. Used for guild join/remove, channel create/delete/update, Bot.get_channel, Bot.guilds.
    guilds = true
    # Members - recommended: false (privileged intent). Used for member join/remove/update, Member.roles, Member.nick, User.name, etc.
    members = false
    # Bans - recommended: false. Used for member ban/unban.
    bans = false
    # Emojis - recommended: false. Used for guild emojis update, Bot.get_emoji, Guild.emojis.
    emojis = false
    # Integrations - recommended: false. Used for guild integrations update.
    integrations = false
    # Webhooks - recommended: false. Used for guild webhooks update.
    webhooks = false
    # Invites - recommended: false. Used for invite create/delete.
    invites = false
    # Voice states - recommended: false. Used for voice state update, VoiceChannel.members, Member.voice.
    voice_states = false
    # Presences - recommended: false (privileged intent). Used for member update (for activities and status), Member.status.
    presences = false
    # Guild messages - recommended: true. Used for message events in guilds.
    guild_messages = true
    # DM messages - recommended: true. Used for message events in DMs.
    dm_messages = true
    # Guild reactions - recommended: false. Used for [raw] reaction add/remove/clear events in guilds.
    guild_reactions = false
    # DM reactions - recommended: false. Used for [raw] reaction add/remove/clear events in DMs.
    dm_reactions = false
    # Guild typing - recommended: false. Used for the typing event in guilds.
    guild_typing = false
    # DM typing - recommended: false. Used for the typing event in Dms.
    dm_typing = false

# Data used to send API requests to whatever service
[bot_listing_api_keys]
    topgg_token = ""  # The token used to post data to top.gg
    discordbotlist_token = ""  # The token used to post data to discordbotlist.com

# Data that's copied directly over to a command
[command_data]
    guild_invite = ""  # A link to be used on !support
    github_link = ""  # A link to be used on !git
    donate_link = ""  # A link to be used on !donate
    invite_command_permissions = []  # args here are passed directly to discord.Permissions. An empty list disabled the invite command
    echo_command_enabled = true  # Whether or not the invite command is enabled
    stats_command_enabled = true  # Whether or not the stats command is enabled
    vote_command_enabled = false  # Whether or not the top.gg vote command is enabled
    updates_channel_id = 0  # The ID of the news channel for the bot

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

# Used to generate the invite link - if not set then will use the bot's ID, which is correct more often than not
[oauth]
    client_id = ""

# This is where you can set up all of your analytics to be sent to GA; automatically disabled if no data is provided
[google_analytics]
    tracking_id = ""  # Tracking ID for your GA instance
    app_name = ""  # The name of your bot - what you want GA to name this traffic source
    document_host = ""  # The (possibly fake) URL you want to tell GA this website is

# It's time for better analytics! Let's give statsd a little try
[statsd]
    host = "127.0.0.1"
    port = 8125  # This is the DataDog default, 9125 is the general statsd default
    [statsd.constant_tags]
        service = ""  # Put your bot name here - leave blank to disable stats collection
"""
