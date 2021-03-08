import asyncio
from datetime import datetime as dt

from discord.ext import commands


class IsNotUpgradeChatSubscriber(commands.CheckFailure):
    """The error raised when the user is missing an UpradeChat subscription."""

    def __init__(self):
        super().__init__("You need to be subscribed via Upgrade.Chat to run this command - see `{ctx.clean_prefix}donate` for more information.")


def is_upgrade_chat_subscriber(*any_item_names):
    """
    A check to see whether a given user is an UpgradeChat subscriber for _any_ of the given item names,
    returning a list of things that they've purchased.
    """

    async def predicate(ctx):

        # See if we're even requesting anything
        if not any_item_names:
            ctx.bot.logger.warning(f"No role tiers input for is_upgrade_chat_subscriber for command {ctx.command.name}")
            return set()

        # Grab all purchased roles by the user
        try:
            purchases = await asyncio.wait_for(ctx.bot.upgrade_chat.get_orders(discord_id=ctx.author.id), timeout=3)
        except asyncio.TimeoutError:
            raise commands.CheckFailure("Upgrade.Chat is currently unable to process my request for subscribers - please try again later.")

        # See if they purchased anything that's correct
        output_items = set()
        for purchase in purchases:
            if purchase.deleted is not None and purchase.deleted > dt.utcnow():
                continue
            for order_item in purchase.order_items:
                product_name = order_item.product_name
                if product_name in any_item_names:
                    output_items.add(product_name)
        if output_items:
            return output_items

        # They didn't purchase anything [valid]
        raise IsNotUpgradeChatSubscriber()

    return commands.check(predicate)
