import asyncio
from datetime import datetime as dt

from discord.ext import commands


class IsNotUpgradeChatSubscriber(commands.CheckFailure):
    """The error raised when the user is missing an UpradeChat subscription."""


def is_upgrade_chat_subscriber(*role_tiers):
    """
    A check to see whether a given user is an UpgradeChat subscriber for any of the given role IDs.
    """

    error = IsNotUpgradeChatSubscriber(
        "You need to be subscribed via Upgrade.Chat to run this command - see `{ctx.clean_prefix}donate` for more information."
    )

    async def predicate(ctx):

        # See if we're even requesting anything
        if not role_tiers:
            return True

        # Grab all the roles that are valid
        all_upgrade_chat_roles = ctx.bot.config.get("upgrade_chat", dict()).get("roles", dict())
        any_required_roles = [o for i, o in all_upgrade_chat_roles.items() if i in role_tiers]
        if not any_required_roles:
            ctx.bot.logger.warning(f"Missing roles for UpgradeChat subscriber check - {role_tiers}")
            return True

        # Grab all purchased roles by the user
        try:
            purchases = asyncio.wait_for(ctx.bot.upgrade_chat.get_orders(discord_id=ctx.author.id), timeout=3)
        except asyncio.TimeoutError:
            raise commands.CheckFailure("Upgrade.Chat is currently unable to process my request for subscribers - please try again later.")

        # See if they purchased anything that's correct
        for purchase in purchases:
            if purchase.deleted is not None and purchase.deleted > dt.utcnow():
                continue
            for order_item in purchase.order_items:
                if not order_item.type == "DISCORD_ROLE":
                    continue
                for role in order_item.discord_roles:
                    if int(role['discord_id']) in any_required_roles:
                        return True

        # They didn't purchase anything [valid]
        raise error

    return commands.check(predicate)
