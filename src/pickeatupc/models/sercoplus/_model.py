"""Sercoplus model module.

TODO: First abstract the sercoplus logic (as a store), them the pc build logic.
TODO: Get thumbnail, price (usd and pen), name, url and stock.
TODO: Use get home method to get all header import urls.
TODO: Don't Repeat Yourself.
"""

from asyncio import Task, create_task, gather

from aiohttp import ClientSession
from price_parser.parser import Price
from pydantic import PositiveInt
from selectolax.parser import HTMLParser
from yarl import URL

from ..._core.config import URLS
from ._constants import ENHANCED_QUERY, MIN_PAGE_COUNT
from ._selectors import EMPTY_PAGE_SECTION, ITEM_DIV, PAGINATION_ANCHOR


class Sercoplus:
    """Sercoplus model class."""

    url: URL = URL(URLS["sercoplus"])

    def __init__(self, session: ClientSession) -> None:
        """Sercoplus model initializer."""
        if not isinstance(session, ClientSession):
            raise TypeError("session is not a ClientSession.")
        self._session: ClientSession = session

    def _get_query(self, page: PositiveInt = 1) -> dict[str, str]:
        """Get query."""
        if not isinstance(page, int) or page < 1:
            raise TypeError("Page must be a positive integer.")
        if page == 1:
            return ENHANCED_QUERY
        return dict(ENHANCED_QUERY, page=str(page))

    def _build_url(self, endpoint: str, page: PositiveInt = 1) -> URL:
        """Build URL."""
        url: URL = self.url / endpoint
        return url.update_query(self._get_query(page))

    def _get_page_count(self, html: HTMLParser) -> PositiveInt:
        """Get page count."""
        if not (anchors := tuple(html.css(PAGINATION_ANCHOR))):
            return MIN_PAGE_COUNT
        last_child_text: str = anchors[-1].text()
        page_count: int = int(last_child_text)
        assert page_count > MIN_PAGE_COUNT
        return page_count

    def _get_search_url(self, value: str, page: PositiveInt = 1) -> URL:
        if len(value) < 3:
            raise ValueError("Value is too short.")
        url: URL = self._build_url("busqueda", page)
        return url.update_query(dict(s=value))

    def _get_items(self, html: HTMLParser) -> tuple[str, ...]:
        """Get items."""
        if html.css_first(EMPTY_PAGE_SECTION):
            return tuple()
        if not (item_divs := tuple(html.css(ITEM_DIV))):
            return tuple()
        return tuple(item.text(separator="\n", strip=True) for item in item_divs)

    async def _get_html(self, url: URL) -> HTMLParser:
        """Get html."""
        async with self._session.get(url, raise_for_status=True) as response:
            payload: bytes = await response.read()
        return HTMLParser(payload)

    async def _get_home(self) -> HTMLParser:
        """Get home."""
        return await self._get_html(self.url)

    # NOTE: Represents in page search, is generic and may be public.
    async def search(self, value: str) -> tuple[str, ...]:
        url: URL = self._get_search_url(value)
        html: HTMLParser = await self._get_html(url)

        page_count: PositiveInt = self._get_page_count(html)
        if page_count == 1:
            return self._get_items(html)

        page_range: range = range(2, page_count + 1)
        urls: tuple[URL, ...]
        urls = tuple(self._get_search_url(value, page) for page in page_range)

        tasks: tuple[Task[HTMLParser], ...]
        tasks = tuple(create_task(self._get_html(url)) for url in urls)
        htmls: tuple[HTMLParser, ...] = tuple(await gather(*tasks))
        return tuple(item for html in htmls for item in self._get_items(html))

    # NOTE represents a private search but with a specific endpoint. it may be called by another public function with specific endpointed urls.
    async def get_items(self, endpoint: str) -> tuple[str, ...]:
        url: URL = self._build_url(endpoint)
        html: HTMLParser = await self._get_html(url)

        page_count: PositiveInt = self._get_page_count(html)
        if page_count == 1:
            return self._get_items(html)

        page_range: range = range(2, page_count + 1)
        urls: tuple[URL, ...]
        urls = tuple(self._build_url(endpoint, page) for page in page_range)

        tasks: tuple[Task[HTMLParser], ...]
        tasks = tuple(create_task(self._get_html(url)) for url in urls)
        htmls: tuple[HTMLParser, ...] = tuple(await gather(*tasks))
        return tuple(item for html in htmls for item in self._get_items(html))
