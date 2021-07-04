import enum
import typing

import discord


class DataLocation(enum.Enum):
    GUILD = enum.auto()
    USER = enum.auto()


class MenuCallbacks(object):

    @staticmethod
    def is_discord_object(item) -> bool:
        return isinstance(
            item,
            (
                discord.TextChannel,
                discord.VoiceChannel,
                discord.Role,
                discord.Member,
                discord.Guild,
                discord.Object,
            )
        )

    @classmethod
    def set_table_column(cls, data_location: DataLocation, table_name: str, column_name: str):
        """
        Returns a wrapper that updates the guild settings table for the bot's database.
        """

        async def wrapper(ctx, data: list):
            sql = """INSERT INTO {0} ({1}, {2}) VALUES ($1, $2) ON CONFLICT ({1}) DO UPDATE SET {2}=excluded.{2}""".format(
                table_name,
                "guild_id" if data_location == DataLocation.GUILD else "user_id" if data_location == DataLocation.USER else None,
                column_name
            )
            data = [i.id if cls.is_discord_object(i) else i for i in data]
            async with ctx.bot.database() as db:
                await db(
                    sql,
                    ctx.guild.id if data_location == DataLocation.GUILD else ctx.author.id if data_location == DataLocation.USER else None,
                    *data,
                )

        return wrapper

    @classmethod
    def set_cache_from_key(cls, data_location: DataLocation, *settings_path):
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.
        """

        def wrapper(ctx, data: list):
            value = data[0]  # If we're here we definitely should only have one datapoint
            if cls.is_discord_object(value):
                value = value.id
            if data_location == DataLocation.GUILD:
                d = ctx.bot.guild_settings[ctx.guild.id]
            elif data_location == DataLocation.USER:
                d = ctx.bot.user_settings[ctx.author.id]
            for i in settings_path[:-1]:
                d = d.setdefault(i, dict())
            d[settings_path[-1]] = value

        return wrapper

    @classmethod
    def set_cache_from_keypair(cls, data_location: DataLocation, *settings_path):
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.
        """

        def wrapper(ctx, data: list):
            key, value = data  # Two datapoints now; that's very sexy
            if cls.is_discord_object(key):
                key = key.id
            if cls.is_discord_object(value):
                value = value.id
            if data_location == DataLocation.GUILD:
                d = ctx.bot.guild_settings[ctx.guild.id]
            elif data_location == DataLocation.USER:
                d = ctx.bot.user_settings[ctx.author.id]
            for i in settings_path:
                d = d.setdefault(i, dict())
            d[key] = value

        return wrapper

    @classmethod
    def set_iterable_dict_cache(cls, data_location: DataLocation, *settings_path):
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.
        """

        def wrapper(ctx, data: list):
            key, value = data  # Two datapoints now; that's very sexy
            if cls.is_discord_object(key):
                key = key.id
            if cls.is_discord_object(value):
                value = value.id
            if data_location == DataLocation.GUILD:
                d = ctx.bot.guild_settings[ctx.guild.id]
            elif data_location == DataLocation.USER:
                d = ctx.bot.user_settings[ctx.author.id]
            for i in settings_path:
                d = d.setdefault(i, dict())
            d[key] = value

        return wrapper

    @classmethod
    def set_iterable_list_cache(cls, data_location: DataLocation, *settings_path):
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.
        """

        def wrapper(ctx, data: list):
            value = data[0]  # If we're here we definitely should only have one datapoint
            if cls.is_discord_object(value):
                value = value.id
            if data_location == DataLocation.GUILD:
                d = ctx.bot.guild_settings[ctx.guild.id]
            elif data_location == DataLocation.USER:
                d = ctx.bot.user_settings[ctx.author.id]
            for i in settings_path[:-1]:
                d = d.setdefault(i, dict())
            settings_list = d.setdefault(settings_path[-1], list())
            if value in settings_list:
                return
            else:
                settings_list.append(value)

        return wrapper

    @classmethod
    def delete_iterable_dict_cache(cls, data_location: DataLocation, *settings_path):
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.
        Gives a nested function that takes a :code:`key` argument that acts as the primary key of the dict.
        """

        def inner(key: str):
            def wrapper(ctx, data: list):
                if data_location == DataLocation.GUILD:
                    d = ctx.bot.guild_settings[ctx.guild.id]
                elif data_location == DataLocation.USER:
                    d = ctx.bot.user_settings[ctx.author.id]
                for i in settings_path:
                    d = d.setdefault(i, dict())
                d.pop(key, None)
            return wrapper
        return inner

    @classmethod
    def delete_iterable_list_cache(cls, data_location: DataLocation, *settings_path):
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.
        Gives a nested function that takes a :code:`value` argument that acts as the data to delete.
        """

        def inner(value: typing.Any):
            def wrapper(ctx, data: list):
                if data_location == DataLocation.GUILD:
                    d = ctx.bot.guild_settings[ctx.guild.id]
                elif data_location == DataLocation.USER:
                    d = ctx.bot.user_settings[ctx.author.id]
                for i in settings_path[:-1]:
                    d = d.setdefault(i, dict())
                settings_list = d.setdefault(settings_path[-1], list())
                if value not in settings_list:
                    return
                else:
                    settings_list.remove(value)
            return wrapper
        return inner
