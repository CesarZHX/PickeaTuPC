"""Sercoplus model module.

TODO: Firs abstract the sercoplus logic (as a store), them the pc build logic.
TODO: Query can also have and page argument that is int  # &page=2
TODO: Get thumbnail, price (usd and pen), name, url, stock.
"""

from re import Pattern, compile

from aiohttp import ClientSession
from price_parser.parser import Price
from selectolax.parser import HTMLParser
from yarl import URL

from .._config import SERCOPLUS_URL
from ._selectors import EMPTY_PAGE, ITEM_DIV, PAGINATION_DIV

_PAGINATION_PATTERN: Pattern[str] = compile(r"Mostrando\s+(\d+)-(\d+)\s+de\s+(\d+)")
_AVAILABLE_QUERY: dict[str, str] = dict(q="Disponibilidad-En%20stock")
_QUERY: dict[str, str] = dict(_AVAILABLE_QUERY, order="product.price.asc")


class Sercoplus:
    """Sercoplus model class."""

    url: URL = SERCOPLUS_URL

    def __init__(self, session: ClientSession) -> None:
        """Sercoplus model initializer."""
        if not isinstance(session, ClientSession):
            raise TypeError("session is not a ClientSession.")
        self._session: ClientSession = session

    def _get_query(self, page: int = 1) -> dict[str, str]:
        """Get query."""
        if not isinstance(page, int):
            raise TypeError("page is not an int.")
        if page < 1:
            raise ValueError("page must be positive.")
        return dict(_QUERY, page=str(page))

    async def _get_page(self, url: URL) -> HTMLParser:
        async with self._session.get(url, raise_for_status=True) as response:
            payload: bytes = await response.read()
        return HTMLParser(payload)

    def _search(self, value: str) -> tuple[str, ...]:
        if len(value) < 3:
            raise ValueError("value is too short.")
        query: dict[str, str] = dict(self._get_query(), controller="search", s=value)
        _url: URL = self.url / "busqueda"
        url: URL = _url.update_query(query)
        raise NotImplementedError

    async def search(self, endpoint: str) -> tuple[str, ...]:
        _url: URL = self.url / endpoint
        url: URL = _url.update_query(self._get_query())
        html_parser: HTMLParser = await self._get_page(url)
        if not (pagination_div := html_parser.css_first(PAGINATION_DIV)):
            return tuple()
        if not (pagination := _PAGINATION_PATTERN.search(pagination_div.text())):
            return tuple()
        first_in_page, last_in_page, last = map(int, pagination.groups())
        # TODO: extract all items across all pages, using pagination to kwnow when to stop.
        items_per_page = (last_in_page + 1) - first_in_page
        pages = last // items_per_page
        if not (items := html_parser.css(ITEM_DIV)):
            if not html_parser.css_first(EMPTY_PAGE):
                raise RuntimeError("Empty page not found.")
        return tuple(item.text(separator="\n", strip=True) for item in items)
