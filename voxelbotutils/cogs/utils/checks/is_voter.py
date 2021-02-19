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

        # Make a function we can wait for to get the information
        async def send_get_request():
            url = "https://top.gg/api/bots/{bot.user.id}/check".format(bot=ctx.bot)
            async with ctx.bot.session.get(url, params={"userId": ctx.author.id}, headers={"Authorization": topgg_token}) as r:
                try:
                    data = await r.json()
                except Exception:
                    raise error
                if r.status != 200:
                    raise error
                return data

        # Try and get the information
        try:
            data = asyncio.wait_for(send_get_request(), timeout=3)
        except asyncio.TimeoutError:
            raise commands.CheckFailure("Top.gg is currently unable to process my request for voters - please try again later.")

        # See if they voted
        if bool(data['voted']):
            return True

        # Oh boy oh jeez oh no
        raise error

    return commands.check(predicate)
