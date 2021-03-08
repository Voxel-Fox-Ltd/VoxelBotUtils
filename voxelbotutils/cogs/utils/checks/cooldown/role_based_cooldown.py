from discord.ext import commands

from .cooldown import Cooldown


class RoleBasedCooldown(Cooldown):
    """
    A cooldown that lets you set a cooldown for a command based on the user's roles.
    """

    _copy_kwargs = ()

    def __init__(self, tiers:dict, **kwargs):
        """
        Args:
            tiers (dict): The dictionary of `{role_id: seconds}` that should be used for this cooldown.
            **kwargs: The default kwargs to be passed to the original cooldown class.
        """
        super().__init__(**kwargs)
        self.tier_cooldowns = tiers  # RoleID: CooldownSeconds

    def predicate(self, ctx:commands.Context):
        """
        Update the cooldown based on the given guild member.
        """

        message = ctx.message
        if message.guild is None:
            return  # Go for the default
        cooldown_seconds = [o for i, o in self.tier_cooldowns.items() if i in message.author._roles]  # Get valid cooldowns
        if not cooldown_seconds:
            return
        self.per = min(cooldown_seconds)  # Set this rate as the minimum form the roles
