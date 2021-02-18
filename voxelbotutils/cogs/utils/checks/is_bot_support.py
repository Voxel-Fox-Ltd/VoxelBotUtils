from discord.ext import commands


class NotBotSupport(commands.MissingRole):
    """The generic error for the bot failing the is_bot_support check"""

    def __init__(self):
        super().__init__("Bot Support Team")


def is_bot_support():
    """
    Checks whether or not the calling user has the bot support role.
    Comes in two flavours: it works as a decorator/check for commands, or you can call it
    as is with a ctx and Member object.
    """

    async def predicate(ctx:commands.Context):
        if ctx.author.id in ctx.bot.owner_ids:
            return True
        if ctx.guild is None:
            raise NotBotSupport()
        if ctx.bot.config.get("bot_support_role_id", 0) in ctx.author._roles or ctx.author.id in ctx.bot.owner_ids:
            return True
        raise NotBotSupport()
    return commands.check(predicate)
