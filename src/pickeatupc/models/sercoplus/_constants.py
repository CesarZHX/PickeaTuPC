"""Sercoplus constants module."""

from pydantic import PositiveInt

_AVAILABLE_QUERY_ITEM: dict[str, str] = dict(q="Disponibilidad-En%20stock")
ENHANCED_QUERY: dict[str, str] = dict(_AVAILABLE_QUERY_ITEM, order="product.price.asc")

MIN_PAGE_COUNT: PositiveInt = 1
