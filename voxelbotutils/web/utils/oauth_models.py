import typing

import discord


class OauthGuild(object):

    def __init__(self, bot, guild_data, user):
        self.id: int = int(guild_data.get("id"))
        self.name: str = guild_data.get("name")
        self.icon: str = guild_data.get("icon")
        self.icon_url: discord.Asset = discord.Asset._from_guild_icon(None, self)
        self.owner_id: int = user.id if guild_data.get("owner") else 0
        self.features: typing.List[str] = guild_data.get("features")
        self._bot: discord.Client = bot

    def is_icon_animated(self) -> bool:
        return self.icon.startswith("a_")

    async def fetch_guild(self) -> discord.Guild:
        try:
            return await self._bot.fetch_guild(self.id)
        except discord.HTTPException:
            return None


class OauthUser(object):

    def __init__(self, user_data):
        self.id: int = int(user_data['id'])
        self.username: str = user_data.get("username")
        self.avatar: str = user_data.get("avatar")
        self.avatar_url: discord.Asset = discord.Asset._from_avatar(None, self)
        self.discriminator: str = user_data.get("discriminator")
        self.public_flags: discord.PublicUserFlags = discord.PublicUserFlags._from_value(user_data.get("public_flags", 0))
        self.locale: str = user_data.get("locale")
        self.mfa_enabled: bool = user_data.get("mfa_enabled", False)

    def is_avatar_animated(self) -> bool:
        return self.avatar.startswith("a_")


class OauthMember(OauthUser):

    def __init__(self, bot, guild_data, user_data):
        super().__init__(user_data)
        self.guild: OauthGuild = OauthGuild(bot, guild_data, self)
        self.guild_permissions: discord.Permissions = discord.Permissions(guild_data['permissions'])
