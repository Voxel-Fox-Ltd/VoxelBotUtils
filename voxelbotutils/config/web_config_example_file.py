web_config_file = """
# These are a few different tokens for Discord bots that you can use at once
# These will all be loaded into the bot as dictionary arguments
# This is fully welcome to be entirely empty
[discord_bots]
    bot_name = "token here"

# Used for the bot's invite and login links
[oauth]
    client_id = ""
    client_secret = ""

# Here's some URLs that the bot will use internally to redirect to
[static_urls]
    login_url = ""  # The url for the bot's login - can be internal (/login) or a real URL

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
"""
