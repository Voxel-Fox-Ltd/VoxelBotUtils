from discord.ext import commands


class BooleanConverter(commands.Converter):
    """
    Converts a given input into a boolean yes/no.
    """

    @classmethod
    async def convert(self, ctx, argument):
        return any([
            argument.lower() in ['y', 'yes', 'true', 'definitely', 'ye', 'ya', 'yas', 'ok', 'okay', '1', 't'],
            argument in ['\N{HEAVY CHECK MARK}', '<:tick_yes:596096897995899097>'],
        ])
