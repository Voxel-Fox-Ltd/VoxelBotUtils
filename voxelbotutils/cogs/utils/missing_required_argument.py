from discord.ext import commands


class MissingRequiredArgumentString(commands.MissingRequiredArgument):
    """
    Used so you can manually throw a missing required argument without having to inspect the function.

    Attributes:
        param (str): The parameter that was missing from the command.
    """

    def __init__(self, param:str):
        self.param: str = param
