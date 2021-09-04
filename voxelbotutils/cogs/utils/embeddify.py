import typing

import discord
from discord.ext import commands


TextDestinations = typing.Union[discord.User, discord.Member, discord.TextChannel]
ContextDestinations = typing.Union[commands.Context, commands.SlashContext]
Destinations = typing.Union[TextDestinations, ContextDestinations]


MISSING = discord.utils.MISSING


class Embeddify:
    """
    A class to handle auto-embeddifying of messages.
    """

    bot: typing.Optional['voxelbotutils.Bot'] = None

    @classmethod
    async def send(
            cls, dest: Destinations, content: typing.Optional[str],
            **kwargs) -> discord.Message:
        return await dest.send(**cls.get_embeddify(dest, content, **kwargs))

    @classmethod
    def get_embeddify(
            cls, dest: Destinations, content: typing.Optional[str] = None, *,
            embed: discord.Embed = None, embeds: typing.List[discord.Embed] = None,
            embeddify: bool = MISSING, **kwargs) -> dict:
        """
        Embeddify your given content.
        """

        # Make sure we have a bot to read the config of
        try:
            assert cls.bot
        except AssertionError:
            return {
                "content": content,
                "embeds": embeds if embeds else [embed] if embed else None,
                **kwargs
            }

        # Initial dataset
        data = {
            "content": content,
            "embeds": [],
            **kwargs,
        }
        if embed and embeds:
            raise ValueError("Can't set embeds and embed")
        if embed:
            data['embeds'].append(embed)
        elif embeds:
            data['embeds'].extend(embeds)

        # If embeddify isn't set, grab from the config
        if embeddify is MISSING:
            embeddify = cls.bot.embeddify

        # See if we're done now
        if embeddify is False:
            return data

        # Slash commands can do anything
        if isinstance(dest, (commands.SlashContext, discord.User, discord.Member)):
            can_send_embeds = True

        # Otherwise we have permissions to check
        else:

            # Grab the channel
            if isinstance(dest, commands.Context):
                channel = dest.channel
            else:
                channel = dest

            # Check permissions
            if isinstance(channel, discord.TextChannel):
                channel_permissions: discord.Permissions = channel.permissions_for(dest.guild.me)  # type: ignore
                can_send_embeds = discord.Permissions(embed_links=True).is_subset(channel_permissions)
            else:
                can_send_embeds = True

        # See if we should bother generating embeddify
        should_generate_embeddify = can_send_embeds and embeddify

        # Can't embed or have no content? Just send it normally
        if not should_generate_embeddify:
            return data

        # Okay it's embed time
        embed = discord.Embed(
            description=data.pop("content"),
            colour=discord.Colour.random() or cls.bot.config.get("embed", dict()).get("colour", 0),
        )
        cls.bot.set_footer_from_config(embed)

        # Reset content
        content = cls.bot.config.get("embed", dict()).get("content", "").format(bot=cls.bot)
        if not content:
            content = None

        # Set author
        author_data = cls.bot.config.get("embed", dict()).get("author", {})
        if author_data.get("enabled", False):
            name = author_data.get("name", "").format(bot=cls.bot) or discord.Embed.Empty
            url = author_data.get("url", "").format(bot=cls.bot) or discord.Embed.Empty
            try:
                icon_url: typing.Optional[str] = cls.bot.user.display_avatar.url  # type: ignore
            except AttributeError:
                icon_url = None
            embed.set_author(name=name, url=url, icon_url=icon_url)

        # And we're done and sick and sexy
        data['embeds'].insert(0, embed)
        return data
