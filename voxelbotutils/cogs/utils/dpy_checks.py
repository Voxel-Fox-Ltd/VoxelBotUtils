from discord.ext import commands

from .interactions.interaction_messageable import InteractionMessageable


def filter_kwargs(d):
    n = {}
    for i, o in d.items():
        if i in ["send_messages", "embed_links", "attach_files"]:
            continue
        n.update({i: o})
    return n


def bot_has_permissions(**kwargs):
    async def predicate(ctx):
        if isinstance(ctx, InteractionMessageable):
            return True
        return await commands.bot_has_permissions(**kwargs).predicate(ctx)
    return commands.check(predicate)


def bot_has_guild_permissions(**kwargs):
    async def predicate(ctx):
        if isinstance(ctx, InteractionMessageable):
            return True
        return await commands.bot_has_guild_permissions(**kwargs).predicate(ctx)
    return commands.check(predicate)
