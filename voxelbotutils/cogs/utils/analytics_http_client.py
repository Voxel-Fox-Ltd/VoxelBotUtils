import re

import aiohttp


class AnalyticsBaseConnector(aiohttp.TCPConnector):
    """Woah sometimes it's nice to send stats requests as well"""

    EVENT_NAMES = {
        ('POST', re.compile(r'/channels/([0-9]{15,23})/messages', re.IGNORECASE)): 'send_message',
        ('GET', re.compile(r'/users/([0-9]{15,23})', re.IGNORECASE)): 'get_user',
        ('GET', re.compile('/users/@me/guilds', re.IGNORECASE)): 'get_guilds',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})', re.IGNORECASE)): 'get_guild',
        ('PUT', re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+?)/@me', re.IGNORECASE)): 'add_reaction',
        ('DELETE', re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})', re.IGNORECASE)): 'delete_message',
        ('GET', re.compile(r'/channels/([0-9]{15,23})', re.IGNORECASE)): 'get_channel',
        ('DELETE', re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})', re.IGNORECASE)): 'kick',
        ('PUT', re.compile(r'/guilds/([0-9]{15,23})/bans/([0-9]{15,23})', re.IGNORECASE)): 'ban',
        ('DELETE', re.compile(r'/guilds/([0-9]{15,23})/bans/([0-9]{15,23})', re.IGNORECASE)): 'unban',
        ('PATCH', re.compile(r'/guilds/([0-9]{15,23})/members/@me/nick', re.IGNORECASE)): 'change_nickname',
        ('PATCH', re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})', re.IGNORECASE)): 'edit_member',
        ('POST', re.compile(r'/channels/([0-9]{15,23})/messages/bulk_delete', re.IGNORECASE)): 'bulk_delete',
        ('PATCH', re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})', re.IGNORECASE)): 'edit_message',
        ('DELETE', re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)/([0-9]{15,23})', re.IGNORECASE)): 'remove_reaction',
        ('DELETE', re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)/@me', re.IGNORECASE)): 'remove_reaction',
        ('GET', re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)', re.IGNORECASE)): 'get_reaction_users',
        ('DELETE', re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions', re.IGNORECASE)): 'clear_reactions',
        ('DELETE', re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)', re.IGNORECASE)): 'clear_single_reaction',
        ('GET', re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})', re.IGNORECASE)): 'get_message',
        ('PATCH', re.compile(r'/channels/([0-9]{15,23})', re.IGNORECASE)): 'edit_channel',
        ('POST', re.compile(r'/guilds/([0-9]{15,23})/channels', re.IGNORECASE)): 'create_channel',
        ('DELETE', re.compile(r'/channels/([0-9]{15,23})', re.IGNORECASE)): 'delete_channel',
        ('PATCH', re.compile(r'/guilds/([0-9]{15,23})', re.IGNORECASE)): 'edit_guild',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})/bans', re.IGNORECASE)): 'get_bans',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})/bans/([0-9]{15,23})', re.IGNORECASE)): 'get_ban',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})/channels', re.IGNORECASE)): 'get_channels',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})/members', re.IGNORECASE)): 'get_members',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})', re.IGNORECASE)): 'get_member',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})/emojis', re.IGNORECASE)): 'get_custom_emojis',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})/emojis/([0-9]{15,23})', re.IGNORECASE)): 'get_custom_emoji',
        ('POST', re.compile(r'/guilds/([0-9]{15,23})/emojis', re.IGNORECASE)): 'create_custom_emoji',
        ('DELETE', re.compile(r'/guilds/([0-9]{15,23})/emojis/([0-9]{15,23})', re.IGNORECASE)): 'delete_custom_emoji',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})/audit-logs', re.IGNORECASE)): 'get_audit_logs',
        ('GET', re.compile(r'/guilds/([0-9]{15,23})/roles', re.IGNORECASE)): 'get_roles',
        ('PATCH', re.compile(r'/guilds/([0-9]{15,23})/roles/([0-9]{15,23})', re.IGNORECASE)): 'edit_role',
        ('DELETE', re.compile(r'/guilds/([0-9]{15,23})/roles/([0-9]{15,23})', re.IGNORECASE)): 'delete_role',
        ('PATCH', re.compile(r'/guilds/([0-9]{15,23})/roles', re.IGNORECASE)): 'move_role_position',
        ('PUT', re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})/roles/([0-9]{15,23})', re.IGNORECASE)): 'add_member_role',
        ('DELETE', re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})/roles/([0-9]{15,23})', re.IGNORECASE)): 'remove_member_role',
        ('PUT', re.compile(r'/channels/([0-9]{15,23})/permissions/{target}', re.IGNORECASE)): 'edit_channel_permissions',
        ('DELETE', re.compile(r'/channels/([0-9]{15,23})/permissions/{target}', re.IGNORECASE)): 'remove_channel_permissions',
    }

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def connect(self, request:aiohttp.ClientRequest, *args, **kwargs):
        for (method, path), event in self.EVENT_NAMES.items():
            if request.method != method:
                continue
            if not path.search(str(request.url)):
                continue
            async with self.bot.stats() as stats:
                stats.increment("discord.http", tags={"endpoint": event})
        return await super().connect(request, *args, **kwargs)
