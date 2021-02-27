import asyncio

from discord.ext import commands


class IsNotVoter(commands.CheckFailure):
    """The error thrown when a particular user is not a voter"""


def is_voter(timeout:float=3.0):
    """
    A check to make sure the author of a given command is a voter on your bot's
    Top.gg page. This only works if a Top.gg token is provided in your config (bot_listing_api_keys.topgg_token)
    and is valid.

    Args:
        timeout (float, optional): The amount of time to wait before considering their API to be down.
    """

    error = IsNotVoter("You need to vote for the bot (`{ctx.clean_prefix}vote`) to be able to run this command.")

    async def predicate(ctx:commands.Context):

        # Get the API token
        topgg_token = ctx.bot.config.get('bot_listing_api_keys', {}).get('topgg_token')
        if not topgg_token:
            raise error

        # Try and get the information
        try:
            voted = asyncio.wait_for(ctx.bot.get_user_topgg_vote(ctx.author.id), timeout=3)
        except asyncio.TimeoutError:
            raise commands.CheckFailure("Top.gg is currently unable to process my request for voters - please try again later.")

        # See if they voted
        if voted:
            return True

        # Oh boy oh jeez oh no
        raise error

    return commands.check(predicate)
