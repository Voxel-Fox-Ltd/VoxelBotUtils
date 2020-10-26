from discord.ext import commands


TOPGG_GET_VOTES_ENDPOINT = "https://top.gg/api/bots/{bot.user.id}/check"


class IsNotVoter(commands.CheckFailure):
    """The error thrown when a particular user is not a voter"""


async def has_user_voted(bot, user_id:int) -> bool:
    """
    Returns whether or not the user with the given ID has voted for the bot on Top.gg.

    Args:
        user_id (int): The ID of the user we want to check

    Returns:
        bool: Whether or not the user voted for the bot
    """

    topgg_token = bot.config.get('bot_listing_api_keys', {}).get('topgg_token')
    if not topgg_token:
        return False
    params = {"userId": user_id}
    headers = {"Authorization": topgg_token}
    async with bot.session.get(TOPGG_GET_VOTES_ENDPOINT.format(bot=bot), params=params, headers=headers) as r:
        try:
            data = await r.json()
        except Exception:
            return False
        if r.status != 200:
            return False
    return bool(data['voted'])


def is_voter():
    """A check to make sure the author of a given command is a voter"""

    async def predicate(ctx:commands.Context):
        if await has_user_voted(ctx.bot, ctx.author.id):
            return True
        raise IsNotVoter("You need to vote for the bot (`{ctx.clean_prefix}vote`) to be able to run this command.")
    return commands.check(predicate)
