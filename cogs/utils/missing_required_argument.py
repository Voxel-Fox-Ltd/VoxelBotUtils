from discord.ext import commands


class MissingRequiredArgumentString(commands.MissingRequiredArgument):
    """Used so you can manually throw a missing required argument without having to inspect the function"""

    def __init__(self, param:str):
        self.param = param
