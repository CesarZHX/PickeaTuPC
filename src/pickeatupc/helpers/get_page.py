from aiohttp import ClientSession
from selectolax.parser import HTMLParser
from yarl import URL


async def get_page(session: ClientSession, url: URL) -> HTMLParser:
    async with session.get(url, raise_for_status=True) as response:
        payload: bytes = await response.read()
    return HTMLParser(payload)
