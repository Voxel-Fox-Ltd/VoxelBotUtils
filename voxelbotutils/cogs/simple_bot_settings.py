import asyncio

import discord
from discord.ext import commands

from . import utils


class BotSettings(utils.Cog):

    @utils.command(add_slash_command=False)
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    @utils.checks.is_config_set('database', 'enabled')
    async def prefix(self, ctx: utils.Context, *, new_prefix: str = None):
        """
        Changes the prefix that the bot uses.
        """

        # See if the prefix was actually specified
        prefix_column = self.bot.config.get('guild_settings_prefix_column', 'prefix')
        if new_prefix is None:
            current_prefix = self.bot.guild_settings[ctx.guild.id][prefix_column] or self.bot.config['default_prefix']
            return await ctx.send(
                f"The current prefix is `{current_prefix}`.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        # See if the user has permission
        try:
            await commands.has_guild_permissions(manage_guild=True).predicate(ctx)
        except Exception:
            return await ctx.send(f"You do not have permission to change the command prefix.")

        # Validate prefix
        if len(new_prefix) > 30:
            return await ctx.send("The maximum length a prefix can be is 30 characters.")

        # Store setting
        self.bot.guild_settings[ctx.guild.id][prefix_column] = new_prefix
        async with self.bot.database() as db:
            await db(
                """INSERT INTO guild_settings (guild_id, {prefix_column}) VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET {prefix_column}=excluded.prefix""".format(prefix_column=prefix_column),
                ctx.guild.id, new_prefix
            )
        await ctx.send(
            f"My prefix has been updated to `{new_prefix}`.",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @utils.command(aliases=['follow'], add_slash_command=False)
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, manage_channels=True)
    @commands.guild_only()
    @utils.checks.is_config_set('command_data', 'updates_channel_id')
    async def updates(self, ctx:utils.Context):
        """
        Get official bot updates from the support server.
        """

        # See if they're sure
        m = await ctx.send(
            (
                f"This will follow the bot's official updates channel from the support server "
                f"(`{ctx.clean_prefix}support`). Would you like to continue?"
            ),
            components=utils.MessageComponents.boolean_buttons(),
        )
        try:
            check = lambda p: p.user.id == ctx.author.id and p.message.id == m.id
            payload = await self.bot.wait_for("component_interaction", check=check, timeout=120)
            await payload.ack()
        except asyncio.TimeoutError:
            try:
                await m.delete()
            except discord.HTTPException:
                pass
            return

        # Cancel follow
        if payload.component.custom_id == "NO":
            return await ctx.send("Alright, cancelling!")

        # Get channel
        channel_id = self.bot.config['command_data']['updates_channel_id']
        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            assert channel.is_news()
        except Exception:
            return await payload.send("I couldn't reach the updates channel!")

        # Follow it
        try:
            await channel.follow(destination=ctx.channel)
        except discord.HTTPException as e:
            return await payload.send(f"I wasn't able to follow the updates channel - {e}")

        # Output message
        try:
            check = lambda m: m.guild and m.guild.id == ctx.guild.id and m.content.endswith(f"#{channel.name}")
            await self.bot.wait_for("message", check=check, timeout=5)
        except asyncio.TimeoutError:
            pass
        return await payload.send("Now following the bot's updates channel!")


def setup(bot: utils.Bot):
    x = BotSettings(bot)
    bot.add_cog(x)
