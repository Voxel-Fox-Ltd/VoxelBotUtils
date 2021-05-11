website_frontend_content = """
from aiohttp.web import HTTPFound, Request, Response, RouteTableDef
from voxelbotutils import web as webutils
import aiohttp_session
import discord
from aiohttp_jinja2 import template


routes = RouteTableDef()
"""

website_backend_content = website_frontend_content.rstrip() + '''


@routes.get('/login_processor')
async def login_processor(request:Request):
    """
    Page the discord login redirects the user to when successfully logged in with Discord.
    """

    v = await webutils.process_discord_login(request)
    if isinstance(v, Response):
        return HTTPFound('/')
    session = await aiohttp_session.get_session(request)
    return HTTPFound(location=session.pop('redirect_on_login', '/'))


@routes.get('/logout')
async def logout(request:Request):
    """
    Destroy the user's login session.
    """

    session = await aiohttp_session.get_session(request)
    session.invalidate()
    return HTTPFound(location='/')


@routes.get('/login')
async def login(request:Request):
    """
    Direct the user to the bot's Oauth login page.
    """

    return HTTPFound(location=webutils.get_discord_login_url(request, "/login_processor"))
'''.replace("from aiohttp_jinja2 import template\n", "")
