from discord.ext import commands


class NotBotSupport(commands.MissingRole):
    """The generic error for the bot failing the is_bot_support check"""

    def __init__(self):
        super().__init__("Bot Support Team")


def is_bot_support():
    """
    Checks whether or not the calling user has the bot support role, as defined in the bot's configuration
    file (bot_support_role_id). As it checks a role ID, this will only work it the command in quesiton is called
    in a guild where the calling user _has_ the given role.
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
