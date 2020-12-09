from discord.ext import commands


class EnumConverter(commands.Converter):
    """
    A converter that only lets users give a certain range of inputs.
    """

    def __init__(self, *valid_inputs, case_insensitive:bool=False):
        self.valid_inputs = valid_inputs
        self.case_insensitive = case_insensitive

    @property
    def backticked_valid_inputs(self):
        return [f"`{i}`" for i in self.valid_inputs]

    async def convert(self, ctx, argument):
        new_arg = argument
        if self.case_insensitive:
            new_arg = argument.lower()
        if new_arg not in self.valid_inputs:
            raise commands.BadArgument("`{0}` is not one of {1}".format(argument, ", ".join(self.backticked_valid_inputs)))
        return argument
