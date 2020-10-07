database_file = """
CREATE TABLE guild_settings IF NOT EXISTS(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30)
);


CREATE TABLE user_settings IF NOT EXISTS(
    user_id BIGINT PRIMARY KEY
);


CREATE TABLE role_list IF NOT EXISTS(
    guild_id BIGINT,
    role_id BIGINT,
    key VARCHAR(50),
    value VARCHAR(50),
    PRIMARY KEY (guild_id, role_id, key)
);


CREATE TABLE channel_list IF NOT EXISTS(
    guild_id BIGINT,
    channel_id BIGINT,
    key VARCHAR(50),
    value VARCHAR(50),
    PRIMARY KEY (guild_id, channel_id, key)
);
"""
