from re import Pattern, compile

from aiohttp import ClientSession
from selectolax.parser import HTMLParser
from yarl import URL

from ._config import SERCOPLUS_URL
from .helpers.get_page import get_page

PAGINATION_PATTERN: Pattern[str] = compile(r"Mostrando\s+(\d+)-(\d+)\s+de\s+(\d+)")

AVAILABLE: dict[str, str] = dict(q="Disponibilidad-En%20stock")
# Query can also have and page argument that is int
QUERY: dict[str, str] = dict(AVAILABLE, order="product.price.asc")
ITEM_DIV: str = "article.item > div.thumbnail-container > div.grid"
EMPTY_PAGE: str = "section.page-not-found"
PAGINATION_DIV: str = "div.tv-pagination-content"
# TODO: Get thumbnail, price (usd and pen), name, url, stock


async def get_sercoplus_products(
    session: ClientSession, endpoint: str
) -> tuple[str, ...]:
    url: URL = SERCOPLUS_URL / endpoint
    html_parser: HTMLParser = await get_page(session, url)
    if not (pagination_div := html_parser.css_first(PAGINATION_DIV)):
        return tuple()
    if not (pagination := PAGINATION_PATTERN.search(pagination_div.text())):
        return tuple()
    first_in_page, last_in_page, last = map(int, pagination.groups())
    pages = range(first_in_page, last_in_page + 1)
    if not (items := html_parser.css(ITEM_DIV)):
        assert html_parser.css_first(EMPTY_PAGE)
    return tuple(item.text(separator="\n", strip=True) for item in items)
