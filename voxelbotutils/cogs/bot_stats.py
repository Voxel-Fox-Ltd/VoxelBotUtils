import asyncio

import discord
from discord.ext import commands

from . import utils
from .. import __version__


class BotStats(utils.Cog):

    @commands.command(aliases=['git', 'code'], cls=utils.Command)
    @utils.checks.is_config_set('command_data', 'github_link')
    @commands.bot_has_permissions(send_messages=True)
    async def github(self, ctx:utils.Context):
        """
        Sends the GitHub Repository link.
        """

        await ctx.send(f"<{self.bot.config['command_data']['github_link']}>")

    @commands.command(cls=utils.Command)
    @commands.bot_has_permissions(send_messages=True)
    @utils.checks.is_config_set('command_data', 'invite_command_permissions')
    async def invite(self, ctx:utils.Context):
        """
        Gives you the bot's invite link.
        """

        invite_permissions = {i: True for i in self.bot.config['command_data']['invite_command_permissions']}
        await ctx.send(f"<{self.bot.get_invite_link(**invite_permissions)}>")

    @commands.command(cls=utils.Command)
    @commands.bot_has_permissions(send_messages=True)
    @utils.checks.is_config_set('command_data', 'vote_command_enabled')
    async def vote(self, ctx:utils.Context):
        """
        Gives you a link to vote for the bot.
        """

        bot_user_id = self.bot.config.get('oauth', {}).get('client_id', None) or self.bot.user.id
        await ctx.send(f"<https://top.gg/bot/{bot_user_id}/vote>")

    @commands.command(aliases=['status', 'botinfo'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @utils.checks.is_config_set('command_data', 'stats_command_enabled')
    async def stats(self, ctx:utils.Context):
        """
        Gives you the stats for the bot.
        """

        # Get creator info
        creator_id = self.bot.config["owners"][0]
        creator = self.bot.get_user(creator_id) or await self.bot.fetch_user(creator_id)

        # Make embed
        embed = utils.Embed(use_random_colour=True)
        embed.set_footer(f"{self.bot.user} - VoxelBotUtils v{__version__}", icon_url=self.bot.user.avatar_url)
        embed.add_field("Creator", f"{creator!s}\n{creator_id}")
        embed.add_field("Library", f"Discord.py {discord.__version__}")
        if self.bot.shard_count != len(self.bot.shard_ids):
            embed.add_field("Approximate Guild Count", int((len(self.bot.guilds) / len(self.bot.shard_ids)) * self.bot.shard_count))
        else:
            embed.add_field("Guild Count", len(self.bot.guilds))
        embed.add_field("Shard Count", self.bot.shard_count)
        embed.add_field("Average WS Latency", f"{(self.bot.latency * 1000):.2f}ms")
        embed.add_field("Coroutines", f"{len([i for i in asyncio.Task.all_tasks() if not i.done()])} running, {len(asyncio.Task.all_tasks())} total.")

        # Get topgg data
        if self.bot.config.get('bot_listing_api_keys', {}).get("topgg_token"):
            params = {"fields": "points,monthlyPoints"}
            headers = {"Authorization": self.bot.config['bot_listing_api_keys']['topgg_token']}
            async with self.bot.session.get(f"https://top.gg/api/bots/{self.bot.user.id}", params=params, headers=headers) as r:
                try:
                    data = await r.json()
                except Exception:
                    data = {}
            if "points" in data and "monthlyPoints" in data:
                embed.add_field("Bot Votes", f"[Top.gg](https://top.gg/bot/{self.bot.user.id}): {data['points']} ({data['monthlyPoints']} this month)")

        # Get discordbotlist data
        if self.bot.config.get('bot_listing_api_keys', {}).get("discordbotlist_token"):
            async with self.bot.session.get(f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}") as r:
                try:
                    data = await r.json()
                except Exception:
                    data = {}
            if "upvotes" in data and "metrics" in data:
                content = {
                    "name": "Bot Votes",
                    "value": f"[DiscordBotList.com](https://discordbotlist.com/bots/{self.bot.user.id}): {data['metrics'].get('upvotes', 0)} ({data['upvotes']} this month)"
                }
                try:
                    current_data = embed.get_field_by_key("Bot Votes")
                    content['value'] = current_data['value'] + '\n' + content['value']
                    embed.edit_field_by_key("Bot Votes", **content)
                except KeyError:
                    embed.add_field(**content)
            elif "upvotes" in data:
                content = {
                    "name": "Bot Votes",
                    "value": f"[DiscordBotList.com](https://discordbotlist.com/bots/{self.bot.user.id}): {data['upvotes']}"
                }
                try:
                    current_data = embed.get_field_by_key("Bot Votes")
                    content['value'] = current_data['value'] + '\n' + content['value']
                    embed.edit_field_by_key("Bot Votes", **content)
                except KeyError:
                    embed.add_field(**content)

        # Send it out wew let's go
        await ctx.send(embed=embed)


def setup(bot:utils.Bot):
    x = BotStats(bot)
    bot.add_cog(x)
