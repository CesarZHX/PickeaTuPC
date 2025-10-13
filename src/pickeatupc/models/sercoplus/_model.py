"""Sercoplus model module.

TODO: First abstract the sercoplus logic (as a store), them the pc build logic.
TODO: Get thumbnail, price (usd and pen), name, url and stock.
TODO: Use get home method to get all header import urls.
TODO: Add page number validation for query module.
TODO: Don't Repeat Yourself.
"""

from asyncio import Task, create_task, gather

from aiohttp import ClientSession
from price_parser.parser import Price
from pydantic import PositiveInt
from selectolax.parser import HTMLParser
from yarl import URL

from ..._core.config import URLS
from .._page_number import PageNumber
from ._query.model import AVAILABLE_PRICE_ORDERED_QUERY, QUERY
from ._selectors import (
    CURRENT_PAGE_ANCHOR,
    EMPTY_PAGE_SECTION,
    ITEM_DIV,
    PAGINATION_ANCHOR,
)


class Sercoplus:
    """Sercoplus model class."""

    url: URL = URL(URLS["sercoplus"])

    def __init__(self, session: ClientSession) -> None:
        """Sercoplus model initializer."""
        if not isinstance(session, ClientSession):
            raise TypeError("session is not a ClientSession.")
        self._session: ClientSession = session

    def _get_query(
        self, page_number: PageNumber = PageNumber.minimun()
    ) -> dict[str, str]:
        """Get query."""
        if page_number.is_minimun():
            return QUERY
        return dict(AVAILABLE_PRICE_ORDERED_QUERY, page=str(page_number))

    def _build_url(self, endpoint: str, page: PageNumber = PageNumber.minimun()) -> URL:
        """Build URL."""
        url: URL = self.url / endpoint
        return url.update_query(self._get_query(page))

    def _get_page_count(self, html: HTMLParser) -> PositiveInt:
        """Get page count."""
        if not (anchors := tuple(html.css(PAGINATION_ANCHOR))):
            return int(PageNumber.minimun())
        last_child_text: str = anchors[-1].text()
        page_count: int = int(last_child_text)
        assert page_count > int(PageNumber.minimun())
        return page_count

    def _get_search_url(
        self, value: str, page: PageNumber = PageNumber.minimun()
    ) -> URL:
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

    def _get_page_number(self, html: HTMLParser) -> PositiveInt:
        """Get current page."""
        if not (current_page_anchor := html.css_first(CURRENT_PAGE_ANCHOR)):
            return 1
        text: str = current_page_anchor.text()
        number: int = int(text)
        assert number > 0
        return number

    async def _get_html(self, url: URL) -> HTMLParser:
        """Get html."""
        async with self._session.get(url, raise_for_status=True) as response:
            payload: bytes = await response.read()
        return HTMLParser(payload)

    async def _get_home(self) -> HTMLParser:
        """Get home."""
        return await self._get_html(self.url)

    def _get_missing_page_range(self, html: HTMLParser) -> tuple[PositiveInt, ...]:
        """Get missing page range."""
        if (page_count := self._get_page_count(html)) == int(PageNumber.minimun()):
            return tuple()
        page_number: PositiveInt = self._get_page_number(html)
        range_stop: PositiveInt = page_count + int(PageNumber.minimun())
        page_range: range = range(int(PageNumber.minimun()), range_stop)
        missing_range: tuple[PositiveInt, ...]
        missing_range = tuple(i for i in page_range if i != page_number)
        assert all(i > 0 for i in missing_range)
        return missing_range

    # NOTE: Represents in page search, is generic and may be public.
    async def search(self, value: str) -> tuple[str, ...]:
        url: URL = self._get_search_url(value)
        html: HTMLParser = await self._get_html(url)

        page_count: PositiveInt = self._get_page_count(html)
        if page_count == 1:
            return self._get_items(html)

        page_range: range = range(2, page_count + 1)
        urls: tuple[URL, ...]
        urls = tuple(
            self._get_search_url(value, PageNumber(page)) for page in page_range
        )

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
        urls = tuple(self._build_url(endpoint, PageNumber(page)) for page in page_range)

        tasks: tuple[Task[HTMLParser], ...]
        tasks = tuple(create_task(self._get_html(url)) for url in urls)
        htmls: tuple[HTMLParser, ...] = tuple(await gather(*tasks))
        return tuple(item for html in htmls for item in self._get_items(html))
