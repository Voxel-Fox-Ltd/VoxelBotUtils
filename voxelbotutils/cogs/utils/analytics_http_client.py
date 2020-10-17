import discord


class AnalyticsHTTPClient(discord.client.HTTPClient):
    """Woah sometimes it's nice to send stats requests as well"""

    bot = None

    def send_message(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.send_message")
            with stats.timeit("discord.api.send_message"):
                return super().send_message(*args, **kwargs)

    def send_files(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.send_message")
            with stats.timeit("discord.api.send_message"):
                return super().send_files(*args, **kwargs)

    def delete_message(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.delete_message")
            with stats.timeit("discord.api.delete_message"):
                return super().delete_message(*args, **kwargs)

    def delete_messages(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.bulk_delete")
            with stats.timeit("discord.api.bulk_delete"):
                return super().delete_messages(*args, **kwargs)

    def edit_message(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.edit_message")
            with stats.timeit("discord.api.edit_message"):
                return super().edit_message(*args, **kwargs)

    def add_reaction(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.add_reaction")
            with stats.timeit("discord.api.add_reaction"):
                return super().add_reaction(*args, **kwargs)

    def remove_reaction(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.remove_reaction")
            with stats.timeit("discord.api.remove_reaction"):
                return super().remove_reaction(*args, **kwargs)

    def remove_own_reaction(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.remove_reaction")
            with stats.timeit("discord.api.remove_reaction"):
                return super().remove_own_reaction(*args, **kwargs)

    def get_reaction_users(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_reaction_users")
            with stats.timeit("discord.api.get_reaction_users"):
                return super().get_reaction_users(*args, **kwargs)

    def clear_reactions(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.clear_reactions")
            with stats.timeit("discord.api.clear_reactions"):
                return super().clear_reactions(*args, **kwargs)

    def clear_single_reaction(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.clear_single_reaction")
            with stats.timeit("discord.api.clear_single_reaction"):
                return super().clear_single_reaction(*args, **kwargs)

    def get_message(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_message")
            with stats.timeit("discord.api.get_message"):
                return super().get_message(*args, **kwargs)

    def get_channel(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_channel")
            with stats.timeit("discord.api.get_channel"):
                return super().get_channel(*args, **kwargs)

    def kick(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.kick")
            with stats.timeit("discord.api.kick"):
                return super().kick(*args, **kwargs)

    def ban(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.ban")
            with stats.timeit("discord.api.ban"):
                return super().ban(*args, **kwargs)

    def unban(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.unban")
            with stats.timeit("discord.api.unban"):
                return super().unban(*args, **kwargs)

    def change_nickname(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.change_nickname")
            with stats.timeit("discord.api.change_nickname"):
                return super().change_nickname(*args, **kwargs)

    def change_my_nickname(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.change_nickname")
            with stats.timeit("discord.api.change_nickname"):
                return super().change_my_nickname(*args, **kwargs)

    def edit_member(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.edit_member")
            with stats.timeit("discord.api.edit_member"):
                return super().edit_member(*args, **kwargs)

    def edit_channel(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.edit_channel")
            with stats.timeit("discord.api.edit_channel"):
                return super().edit_channel(*args, **kwargs)

    def create_channel(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.create_channel")
            with stats.timeit("discord.api.create_channel"):
                return super().create_channel(*args, **kwargs)

    def delete_channel(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.delete_channel")
            with stats.timeit("discord.api.delete_channel"):
                return super().delete_channel(*args, **kwargs)

    def get_guilds(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_guilds")
            with stats.timeit("discord.api.get_guilds"):
                return super().get_guilds(*args, **kwargs)

    def get_guild(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_guild")
            with stats.timeit("discord.api.get_guild"):
                return super().get_guild(*args, **kwargs)

    def create_guild(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.create_guild")
            with stats.timeit("discord.api.create_guild"):
                return super().create_guild(*args, **kwargs)

    def edit_guild(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.edit_guild")
            with stats.timeit("discord.api.edit_guild"):
                return super().edit_guild(*args, **kwargs)

    def get_bans(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_bans")
            with stats.timeit("discord.api.get_bans"):
                return super().get_bans(*args, **kwargs)

    def get_ban(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_ban")
            with stats.timeit("discord.api.get_ban"):
                return super().get_ban(*args, **kwargs)

    def get_all_guild_channels(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_all_guild_channels")
            with stats.timeit("discord.api.get_all_guild_channels"):
                return super().get_all_guild_channels(*args, **kwargs)

    def get_members(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_members")
            with stats.timeit("discord.api.get_members"):
                return super().get_members(*args, **kwargs)

    def get_member(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_member")
            with stats.timeit("discord.api.get_member"):
                return super().get_member(*args, **kwargs)

    def get_all_custom_emojis(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_all_custom_emojis")
            with stats.timeit("discord.api.get_all_custom_emojis"):
                return super().get_all_custom_emojis(*args, **kwargs)

    def get_custom_emoji(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_custom_emoji")
            with stats.timeit("discord.api.get_custom_emoji"):
                return super().get_custom_emoji(*args, **kwargs)

    def create_custom_emoji(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.create_custom_emoji")
            with stats.timeit("discord.api.create_custom_emoji"):
                return super().create_custom_emoji(*args, **kwargs)

    def delete_custom_emoji(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.delete_custom_emoji")
            with stats.timeit("discord.api.delete_custom_emoji"):
                return super().delete_custom_emoji(*args, **kwargs)

    def get_audit_logs(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_audit_logs")
            with stats.timeit("discord.api.get_audit_logs"):
                return super().get_audit_logs(*args, **kwargs)

    def get_invite(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_invite")
            with stats.timeit("discord.api.get_invite"):
                return super().get_invite(*args, **kwargs)

    def get_roles(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_roles")
            with stats.timeit("discord.api.get_roles"):
                return super().get_roles(*args, **kwargs)

    def edit_role(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.edit_role")
            with stats.timeit("discord.api.edit_role"):
                return super().edit_role(*args, **kwargs)

    def delete_role(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.delete_role")
            with stats.timeit("discord.api.delete_role"):
                return super().delete_role(*args, **kwargs)

    def create_role(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.create_role")
            with stats.timeit("discord.api.create_role"):
                return super().create_role(*args, **kwargs)

    def move_role_position(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.move_role_position")
            with stats.timeit("discord.api.move_role_position"):
                return super().move_role_position(*args, **kwargs)

    def add_role(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.add_role")
            with stats.timeit("discord.api.add_role"):
                return super().add_role(*args, **kwargs)

    def remove_role(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.remove_role")
            with stats.timeit("discord.api.remove_role"):
                return super().remove_role(*args, **kwargs)

    def edit_channel_permissions(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.edit_channel_permissions")
            with stats.timeit("discord.api.edit_channel_permissions"):
                return super().edit_channel_permissions(*args, **kwargs)

    def delete_channel_permissions(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.delete_channel_permissions")
            with stats.timeit("discord.api.delete_channel_permissions"):
                return super().delete_channel_permissions(*args, **kwargs)

    def get_user(self, *args, **kwargs):
        async with self.bot.stats() as stats:
            stats.increment("discord.api.get_user")
            with stats.timeit("discord.api.get_user"):
                return super().get_user(*args, **kwargs)
