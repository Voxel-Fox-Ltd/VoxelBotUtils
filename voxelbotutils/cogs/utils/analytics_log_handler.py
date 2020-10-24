import re
import logging


class AnalyticsLogHandler(logging.Handler):
    """Woah sometimes it's nice to send stats requests as well"""

    EVENT_NAMES = {
        "GET": {
            re.compile(r'/users/([0-9]{15,23})', re.IGNORECASE): 'get_user',
            re.compile(r'/users/@me/guilds', re.IGNORECASE): 'get_guilds',
            re.compile(r'/guilds/([0-9]{15,23})', re.IGNORECASE): 'get_guild',
            re.compile(r'/channels/([0-9]{15,23})', re.IGNORECASE): 'get_channel',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)', re.IGNORECASE): 'get_reaction_users',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})', re.IGNORECASE): 'get_message',
            re.compile(r'/guilds/([0-9]{15,23})/bans', re.IGNORECASE): 'get_bans',
            re.compile(r'/guilds/([0-9]{15,23})/bans/([0-9]{15,23})', re.IGNORECASE): 'get_ban',
            re.compile(r'/guilds/([0-9]{15,23})/channels', re.IGNORECASE): 'get_channels',
            re.compile(r'/guilds/([0-9]{15,23})/members', re.IGNORECASE): 'get_members',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})', re.IGNORECASE): 'get_member',
            re.compile(r'/guilds/([0-9]{15,23})/emojis', re.IGNORECASE): 'get_custom_emojis',
            re.compile(r'/guilds/([0-9]{15,23})/emojis/([0-9]{15,23})', re.IGNORECASE): 'get_custom_emoji',
            re.compile(r'/guilds/([0-9]{15,23})/audit-logs', re.IGNORECASE): 'get_audit_logs',
            re.compile(r'/guilds/([0-9]{15,23})/roles', re.IGNORECASE): 'get_roles',
        },
        "POST": {
            re.compile(r'/channels/([0-9]{15,23})/messages', re.IGNORECASE): 'send_message',
            re.compile(r'/channels/([0-9]{15,23})/messages/bulk_delete', re.IGNORECASE): 'bulk_delete',
            re.compile(r'/guilds/([0-9]{15,23})/channels', re.IGNORECASE): 'create_channel',
            re.compile(r'/guilds/([0-9]{15,23})/emojis', re.IGNORECASE): 'create_custom_emoji',
        },
        "PUT": {
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+?)/@me', re.IGNORECASE): 'add_reaction',
            re.compile(r'/guilds/([0-9]{15,23})/bans/([0-9]{15,23})', re.IGNORECASE): 'ban',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})/roles/([0-9]{15,23})', re.IGNORECASE): 'add_member_role',
            re.compile(r'/channels/([0-9]{15,23})/permissions/{target}', re.IGNORECASE): 'edit_channel_permissions',
        },
        "DELETE": {
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})', re.IGNORECASE): 'delete_message',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})', re.IGNORECASE): 'kick',
            re.compile(r'/guilds/([0-9]{15,23})/bans/([0-9]{15,23})', re.IGNORECASE): 'unban',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)/([0-9]{15,23})', re.IGNORECASE): 'remove_reaction',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)/@me', re.IGNORECASE): 'remove_reaction',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions', re.IGNORECASE): 'clear_reactions',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)', re.IGNORECASE): 'clear_single_reaction',
            re.compile(r'/channels/([0-9]{15,23})', re.IGNORECASE): 'delete_channel',
            re.compile(r'/guilds/([0-9]{15,23})/emojis/([0-9]{15,23})', re.IGNORECASE): 'delete_custom_emoji',
            re.compile(r'/guilds/([0-9]{15,23})/roles/([0-9]{15,23})', re.IGNORECASE): 'delete_role',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})/roles/([0-9]{15,23})', re.IGNORECASE): 'remove_member_role',
            re.compile(r'/channels/([0-9]{15,23})/permissions/{target}', re.IGNORECASE): 'remove_channel_permissions',
        },
        "PATCH": {
            re.compile(r'/guilds/([0-9]{15,23})/members/@me/nick', re.IGNORECASE): 'change_nickname',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})', re.IGNORECASE): 'edit_member',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})', re.IGNORECASE): 'edit_message',
            re.compile(r'/channels/([0-9]{15,23})', re.IGNORECASE): 'edit_channel',
            re.compile(r'/guilds/([0-9]{15,23})', re.IGNORECASE): 'edit_guild',
            re.compile(r'/guilds/([0-9]{15,23})/roles/([0-9]{15,23})', re.IGNORECASE): 'edit_role',
            re.compile(r'/guilds/([0-9]{15,23})/roles', re.IGNORECASE): 'move_role_position',
        },
    }
    MESSAGE_DECONSTRUCTOR = re.compile(r"^(?P<method>.+) https://discord(:?app)?.(?:com|gg)/api/v\d(?P<endpoint>.+) with (?P<payload>.+) has returned (?P<status>\d+)$")

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    @classmethod
    def get_event_name(cls, method:str, url:str) -> str:
        possible_endpoints = cls.EVENT_NAMES.get(method.upper(), {})
        for endpoint_regex, event_name in possible_endpoints.items():
            if endpoint_regex.search(str(url)):
                return event_name
        return None

    def handle(self, record:logging.LogRecord):
        message = record.getMessage()
        self.bot.loop.create_task(self.log_response(message))
        return super().handle(record)

    async def log_response(self, message):
        match = self.MESSAGE_DECONSTRUCTOR.search(message)
        if match is None:
            return
        event_name = self.get_event_name(match.group("method"), match.group("endpoint"))
        if event_name is None:
            return
        async with self.bot.stats() as stats:
            stats.increment("discord.http", tags={"endpoint": event_name, "status_code": int(match.group("status"))})
