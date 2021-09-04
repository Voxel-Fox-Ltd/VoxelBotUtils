from . import runner  # noqa
from .cogs.utils import *  # noqa


def _web_extras_installed():
    try:
        import cryptography  # noqa
        import aiohttp_jinja2  # noqa
        import aiohttp_session  # noqa
        import jinja2  # noqa
        import markdown  # noqa
        import htmlmin  # noqa
    except ImportError:
        return False
    return True


if _web_extras_installed():
    from . import web
else:
    web = None

__version__ = "0.7.3a"
