import discord


class AnalyticsHTTPClient(discord.client.HTTPClient):
    """Woah sometimes it's nice to send stats requests as well"""

    bot = None

    EVENT_NAMES = {
        ('POST', '/channels/{channel_id}/messages'): 'send_message',
        ('DELETE', '/channels/{channel_id}/messages/{message_id}'): 'delete_message',
        ('POST', '/channels/{channel_id}/messages/bulk_delete'): 'bulk_delete',
        ('PATCH', '/channels/{channel_id}/messages/{message_id}'): 'edit_message',
        ('PUT', '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'): 'add_reaction',
        ('DELETE', '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{member_id}'): 'remove_reaction',
        ('DELETE', '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'): 'remove_reaction',
        ('GET', '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}'): 'get_reaction_users',
        ('DELETE', '/channels/{channel_id}/messages/{message_id}/reactions'): 'clear_reactions',
        ('DELETE', '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}'): 'clear_single_reaction',
        ('GET', '/channels/{channel_id}/messages/{message_id}'): 'get_message',
        ('GET', '/channels/{channel_id}'): 'get_channel',
        ('DELETE', '/guilds/{guild_id}/members/{user_id}'): 'kick',
        ('PUT', '/guilds/{guild_id}/bans/{user_id}'): 'ban',
        ('DELETE', '/guilds/{guild_id}/bans/{user_id}'): 'unban',
        ('PATCH', '/guilds/{guild_id}/members/@me/nick'): 'change_nickname',
        ('PATCH', '/guilds/{guild_id}/members/{user_id}'): 'edit_member',
        ('PATCH', '/channels/{channel_id}'): 'edit_channel',
        ('POST', '/guilds/{guild_id}/channels'): 'create_channel',
        ('DELETE', '/channels/{channel_id}'): 'delete_channel',
        ('GET', '/users/@me/guilds'): 'get_guilds',
        ('GET', '/guilds/{guild_id}'): 'get_guild',
        ('PATCH', '/guilds/{guild_id}'): 'edit_guild',
        ('GET', '/guilds/{guild_id}/bans'): 'get_bans',
        ('GET', '/guilds/{guild_id}/bans/{user_id}'): 'get_ban',
        ('GET', '/guilds/{guild_id}/channels'): 'get_channels',
        ('GET', '/guilds/{guild_id}/members'): 'get_members',
        ('GET', '/guilds/{guild_id}/members/{member_id}'): 'get_member',
        ('GET', '/guilds/{guild_id}/emojis'): 'get_custom_emojis',
        ('GET', '/guilds/{guild_id}/emojis/{emoji_id}'): 'get_custom_emoji',
        ('POST', '/guilds/{guild_id}/emojis'): 'create_custom_emoji',
        ('DELETE', '/guilds/{guild_id}/emojis/{emoji_id}'): 'delete_custom_emoji',
        ('GET', '/guilds/{guild_id}/audit-logs'): 'get_audit_logs',
        ('GET', '/guilds/{guild_id}/roles'): 'get_roles',
        ('PATCH', '/guilds/{guild_id}/roles/{role_id}'): 'edit_role',
        ('DELETE', '/guilds/{guild_id}/roles/{role_id}'): 'delete_role',
        ('PATCH', '/guilds/{guild_id}/roles'): 'move_role_position',
        ('PUT', '/guilds/{guild_id}/members/{user_id}/roles/{role_id}'): 'add_member_role',
        ('DELETE', '/guilds/{guild_id}/members/{user_id}/roles/{role_id}'): 'remove_member_role',
        ('PUT', '/channels/{channel_id}/permissions/{target}'): 'edit_channel_permissions',
        ('DELETE', '/channels/{channel_id}/permissions/{target}'): 'remove_channel_permissions',
        ('GET', '/users/{user_id}'): 'get_user',
    }

    @classmethod
    def from_http_client(cls, client:discord.client.HTTPClient):
        v = cls(
            connector=client.connector,
            proxy=client.proxy,
            proxy_auth=client.proxy_auth,
            loop=client.loop,
            unsync_clock=not client.use_clock,
        )
        v.__session = client.__session
        v._locks = client._locks
        v._global_over = client._global_over
        v.token = client.token
        v.bot_token = client.bot_token
        v.user_agent = client.user_agent
        return v

    async def request(self, route, *args, **kwargs):
        stats_route_name = self.EVENT_NAMES.get((route.path, route.method), None)
        if stats_route_name:
            async with self.bot.stats() as stats:
                stats.increment(f"discord.api.{stats_route_name}")
        return await super().request(route, *args, **kwargs)
