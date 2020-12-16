import math
import re
from datetime import timedelta

from discord.ext import commands


class InvalidTimeDuration(commands.BadArgument):
    """
    A conversion error for time durations.

    Args:
        value (str): Description

    Attributes:
        value (str): The value that was given that failed to parse.
    """

    def __init__(self, value:str):
        self.value: str = value

    def __str__(self):
        return f"The value `{self.value}` could not be converted to a valid time duration."


class TimeValue(object):
    """
    An object that nicely converts an integer value into an easily readable string.

    Attributes:
        duration (int): The entire duration, in seconds, of the timevalue object.
        years (int): The number of years that the timevalue object represents.
        days (int): The number of days that the timevalue object represents.
        hours (int): The number of hours that the timevalue object represents.
        minutes (int): The number of minutes that the timevalue object represents.
        seconds (int): The number of seconds that the timevalue object represents.
        clean_spaced (str): A string form of the timevalue object in form "10 hours 3 minutes".
        clean_full (str): A string form of the timevalue object in form "10h 3m".
        clean (str): A string form of the timevalue object in form "10h3m".
        delta (datetime.timedelta): A timedelta for the entire timevalue object.
    """

    TIME_VALUE_REGEX = re.compile(r"^(?:(?P<years>\d+)y)? *(?:(?P<weeks>\d+)w)? *(?:(?P<days>\d+)d)? *(?:(?P<hours>\d+)h)? *(?:(?P<minutes>\d+)m)? *(?:(?P<seconds>\d+)s)?$")
    MAX_SIZE = 0b1111111111111111111111111111111  # 2**31 - this is about 68 years so anything above this is a bit...... much

    def __init__(self, duration:float):
        """
        Args:
            duration (float): The duration to be converted.

        Warning:
            Provided values will be rounded up to the nearest integer.

        Raises:
            InvalidTimeDuration: If the provided time duration was invalid.
        """

        self.duration: int = math.ceil(duration)
        remaining = self.duration

        self.years, remaining = self.get_quotient_and_remainder(remaining, 60 * 60 * 24 * 365)
        self.days, remaining = self.get_quotient_and_remainder(remaining, 60 * 60 * 24)
        self.hours, remaining = self.get_quotient_and_remainder(remaining, 60 * 60)
        self.minutes, remaining = self.get_quotient_and_remainder(remaining, 60)
        self.seconds = remaining

        self.clean_spaced = ' '.join([i for i in [
            f"{self.years}y" if self.years > 0 else None,
            f"{self.days}d" if self.days > 0 else None,
            f"{self.hours}h" if self.hours > 0 else None,
            f"{self.minutes}m" if self.minutes > 0 else None,
            f"{self.seconds}s" if self.seconds > 0 else None,
        ] if i])

        self.clean_full = ' '.join([i for i in [
            f"{self.years} years" if self.years > 0 else None,
            f"{self.days} days" if self.days > 0 else None,
            f"{self.hours} hours" if self.hours > 0 else None,
            f"{self.minutes} minutes" if self.minutes > 0 else None,
            f"{self.seconds} seconds" if self.seconds > 0 else None,
        ] if i])

        if self.duration > self.MAX_SIZE:
            raise InvalidTimeDuration(self.clean)

        self.clean = self.clean_spaced.replace(" ", "")
        self.delta = timedelta(seconds=self.duration)

    @staticmethod
    def get_quotient_and_remainder(value:int, divisor:int):
        """
        A divmod wrapper that just catches a zero division error.
        """

        try:
            return divmod(value, divisor)
        except ZeroDivisionError:
            return 0, value

    def __str__(self):
        return self.clean

    def __repr__(self):
        return f"{self.__class__.__name__}.parse('{self.clean}')"

    @classmethod
    async def convert(cls, ctx:commands.Context, value:str) -> 'TimeValue':
        """
        Takes a value (1h/30m/10s/2d etc) and returns a TimeValue instance with the duration. Provided for use of the Discord.py module.

        Args:
            ctx (commands.Context): The current context object that we want to convert under.
            value (str): The value string to be converted.

        Returns:
            TimeValue: A time value instance.

        No Longer Raises:
            InvalidTimeDuration: If the time could not be successfully converted.
        """

        return cls.parse(value)

    @classmethod
    def parse(cls, value:str) -> 'TimeValue':
        """
        Takes a value (1h/30m/10s/2d etc) and returns a TimeValue instance with the duration.

        Args:
            value (str): The value string to be converted.

        Returns:
            TimeValue: A time value instance.

        Raises:
            InvalidTimeDuration: If the time could not be successfully converted.
        """

        match = cls.TIME_VALUE_REGEX.search(value)
        if match is None:
            raise InvalidTimeDuration(value)
        duration = 0

        if match.group('years'):
            duration += int(match.group('years')) * 60 * 60 * 24 * 365
        if match.group('weeks'):
            duration += int(match.group('weeks')) * 60 * 60 * 24 * 7
        if match.group('days'):
            duration += int(match.group('days')) * 60 * 60 * 24
        if match.group('hours'):
            duration += int(match.group('hours')) * 60 * 60
        if match.group('minutes'):
            duration += int(match.group('minutes')) * 60
        if match.group('seconds'):
            duration += int(match.group('seconds'))
        return cls(duration)
