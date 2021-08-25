import voxelbotutils as vbu


class ButtonCommandRedirect(vbu.Cog):

    @vbu.Cog.listener()
    async def on_component_interaction(self, payload: vbu.ComponentInteractionPayload):
        if not payload.component.custom_id.startswith("RUNCOMMAND"):
            return
        command_name = payload.component.custom_id[len("RUNCOMMAND "):]
        command = self.bot.get_command(command_name)
        if command:
            await payload.defer()
            payload.author = payload.user
            if command.cog:
                await command.callback(command.cog, payload)
            else:
                await command.callback(payload)


def setup(bot: vbu.Bot):
    x = ButtonCommandRedirect(bot)
    bot.add_cog(x)
