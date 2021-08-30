import discord
from discord.ext import commands

from . import utils as vbu


class InteractionHandler(vbu.Cog):

    @vbu.Cog.listener()
    async def on_component_interaction(self, interaction: discord.Interaction):
        if not interaction.component.custom_id.startswith("RUNCOMMAND"):
            return
        command_name = interaction.component.custom_id[len("RUNCOMMAND "):]
        command = self.bot.get_command(command_name)
        ctx = await self.bot.get_slash_context(interaction=interaction)
        ctx.invoked_with = command_name
        ctx.command = command
    	await self.bot.invoke(ctx)


def setup(bot: vbu.Bot):
	x = InteractionHandler(bot)
	bot.add_cog(x)
