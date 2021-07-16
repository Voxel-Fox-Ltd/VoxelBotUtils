from datetime import datetime as dt


class TimeFormatter(object):
    """
    A Python datetime formatter.

    Attributes:
        short_time (str): The given time formatted as "14:11".
        long_time (str): The given time formatted as "14:11:44".
        number_date (str): The given time formatted as "06/07/2021".
        short_date (str): The given time formatted as "6 July 2021".
        short_datetime (str): The given time formatted as "6 July 2021 14:11".
        long_datetime (str): The given time formatted as "Tuesday, 6 July 2021 14:11".
        relative_time (str): The given time formatted as "10 hours ago".
    """

    def __init__(self, time: dt):
        """
        Params:
            time (dt): The time that you want to format.
        """

        self.time = time

    def __str__(self):
        return f"<t:{int(self.time.timestamp())}>"

    @property
    def _fs(self):
        return f"<t:{int(self.time.timestamp())}:{{}}>"

    short_time = property(lambda self: self._fs.format("t"))  # 14:11
    long_time = property(lambda self: self._fs.format("T"))  # 14:11:44
    number_date = property(lambda self: self._fs.format("d"))  # 06/07/2021
    short_date = property(lambda self: self._fs.format("D"))  # 6 July 2021
    short_datetime = property(lambda self: self._fs.format("f"))  # 6 July 2021 14:11 (default)
    long_datetime = property(lambda self: self._fs.format("F"))  # Tuesday, 6 July 2021 14:11
    relative_time = property(lambda self: self._fs.format("R"))  # 10 hours ago
