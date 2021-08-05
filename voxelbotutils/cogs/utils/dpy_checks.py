from discord.ext import commands

from .interactions.interaction_messageable import InteractionMessageable


def bot_has_permissions(*args, **kwargs):
    async def predicate(ctx):
        if isinstasnce(ctx, InteractionMessageable):
            return True
        return await commands.bot_has_permissions(*args, **kwargs).predicate(ctx)
    return commands.check(predicate)


def bot_has_guild_permissions(*args, **kwargs):
    async def predicate(ctx):
        if isinstasnce(ctx, InteractionMessageable):
            return True
        return await commands.bot_has_guild_permissions(*args, **kwargs).predicate(ctx)
    return commands.check(predicate)
