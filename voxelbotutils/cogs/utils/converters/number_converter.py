import re

from discord.ext import commands


class NumberConverter(int):

    @classmethod
    async def convert(cls, ctx, value):
        match = re.search(r"^(\d+(?:\.\d+)?)([kmb])$", value)
        if not match:
            raise commands.BadArgument()
        v = float(match.group(1))
        m = {'k': 10 ** 3, 'm': 10 ** 6, 'b': 10 ** 9}[match.group(2)]
        return cls(v * m)
