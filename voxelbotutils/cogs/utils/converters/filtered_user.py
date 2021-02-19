from discord.ext import commands


class FilteredUser(commands.UserConverter):

    def __init__(self, *, allow_author:bool=False, allow_bots:bool=False):
        super().__init__()
        self.allow_author = allow_author
        self.allow_bots = allow_bots

    async def convert(self, ctx, argument):
        m = await super().convert(ctx, argument)
        if self.allow_author is False and ctx.author.id == m.id:
            raise commands.BadArgument("You can't run this command on yourself.")
        if self.allow_bots is False and m.bot:
            raise commands.BadArgument("You can't run this command on bots.")
        return m


class FilteredMember(commands.MemberConverter):

    def __init__(self, *, allow_author:bool=False, allow_bots:bool=False):
        super().__init__()
        self.allow_author = allow_author
        self.allow_bots = allow_bots

    async def convert(self, ctx, argument):
        m = await super().convert(ctx, argument)
        if self.allow_author is False and ctx.author.id == m.id:
            raise commands.BadArgument("You can't run this command on yourself.")
        if self.allow_bots is False and m.bot:
            raise commands.BadArgument("You can't run this command on bots.")
        return m
