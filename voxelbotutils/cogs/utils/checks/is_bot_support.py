from discord.ext import commands


class NotBotSupport(commands.MissingRole):
    """The generic error for the bot failing the is_bot_support check"""

    def __init__(self):
        super().__init__("Bot Support Team")


def is_bot_support():
    """The check for whether the bot has cached all of its data yet"""

    async def predicate(ctx:commands.Context):
        if ctx.guild is None:
            raise NotBotSupport()
        if ctx.bot.config.get("bot_support_role_id", 0) in ctx.author._roles or ctx.author.id in ctx.bot.owner_ids:
            return True
        raise NotBotSupport()
    return commands.check(predicate)
