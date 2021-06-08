import typing

import discord


class OauthGuild(object):
    """
    A guild object from an oauth integration.

    Attributes:
        id (int): The ID of the guild.
        name (str): The name of the guild.
        icon (str): The guild's icon hash.
        icon_url (discord.Asset): The guild's icon.
        owner_id (int): The ID of the owner for the guild.
            This will either be the ID of the authenticated user or `0`.
        features (typing.List[str]): A list of features that the guild has.sa
    """

    def __init__(self, bot, guild_data, user):
        self.id: int = int(guild_data.get("id"))
        self.name: str = guild_data.get("name")
        self.icon: str = guild_data.get("icon")
        self.owner_id: int = user.id if guild_data.get("owner") else 0
        self.features: typing.List[str] = guild_data.get("features")
        self._bot: discord.Client = bot

    def is_icon_animated(self) -> bool:
        return self.icon.startswith("a_")

    @property
    def icon_url(self):
        return self.icon_url_as()

    def icon_url_as(self, *, format=None, static_format='webp', size=1024):
        return discord.Asset._from_guild_icon(None, self, format=format, static_format=static_format, size=size)

    async def fetch_guild(self, bot=None) -> typing.Optional[discord.Guild]:
        """
        Fetch the original :class:`discord.Guild` object from the API using the authentication from the
        bot given.

        Args:
            bot: The bot object that you want to use to fetch the guild.

        Returns:
            typing.Optional[discord.Guild]: The guild instance.
        """

        bot = bot or self._bot
        try:
            return await bot.fetch_guild(self.id)
        except discord.HTTPException:
            return None


class OauthUser(object):
    """
    A user object from an oauth integration.

    Attributes:
        id (int): The ID of the user.
        username (str): The user's username.
        avatar (str): The user's avatar hash.
        avatar_url (discord.Asset): The user's avatar.
        discriminator (str): The user's discrimiator.
        public_flags (discord.PublicUserFlags): The user's public flags.
        locale (str): The locale of the user.
        mfa_enabled (bool): Whether or not the user has MFA enabled.
    """

    def __init__(self, user_data):
        self.id: int = int(user_data['id'])
        self.username: str = user_data.get("username")
        self.avatar: str = user_data.get("avatar")
        self.discriminator: str = user_data.get("discriminator")
        self.public_flags: discord.PublicUserFlags = discord.PublicUserFlags._from_value(user_data.get("public_flags", 0))
        self.locale: str = user_data.get("locale")
        self.mfa_enabled: bool = user_data.get("mfa_enabled", False)

    def is_avatar_animated(self) -> bool:
        return self.avatar.startswith("a_")

    @property
    def avatar_url(self):
        return self.avatar_url_as()

    def avatar_url_as(self, *, format=None, static_format='webp', size=1024):
        return discord.Asset._from_avatar(None, self, format=format, static_format=static_format, size=size)


class OauthMember(OauthUser):
    """
    A user object from an oauth integration.

    Attributes:
        id (int): The ID of the user.
        username (str): The user's username.
        avatar (str): The user's avatar hash.
        avatar_url (discord.Asset): The user's avatar.
        discriminator (str): The user's discrimiator.
        public_flags (discord.PublicUserFlags): The user's public flags.
        locale (str): The locale of the user.
        mfa_enabled (bool): Whether or not the user has MFA enabled.
        guild (OauthGuild): The guild object that this member is a part of.
        guild_permissions (discord.Permissions): The permissions that this member has on the guild.
    """

    def __init__(self, bot, guild_data, user_data):
        super().__init__(user_data)
        self.guild: OauthGuild = OauthGuild(bot, guild_data, self)
        self.guild_permissions: discord.Permissions = discord.Permissions(guild_data['permissions'])
