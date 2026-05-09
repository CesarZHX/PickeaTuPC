"""Query module."""

from pydantic import Field, PositiveInt

from .availability import AvailabilityQuery, AvailableQuery
from .base import FrozenQueryConstructor
from .order import OrderQuery, PriceQuery


class Query(FrozenQueryConstructor):
    """Query model."""

    availability: AvailabilityQuery = Field(default_factory=AvailabilityQuery)
    order: OrderQuery = Field(default_factory=OrderQuery)
    page: PositiveInt = Field(default=1)

    def build(self) -> dict[str, str]:
        """Build query."""
        query: dict[str, str] = self.availability.build() | self.order.build()
        return query | dict(page=str(self.page))

    def is_in_first_page(self) -> bool:
        """Check if query is in first page."""
        return self.page == 1


class AvailablePriceOrderedQuery(Query):
    """Available price ordered query model."""

    availability: AvailabilityQuery = Field(default_factory=AvailableQuery)
    order: OrderQuery = Field(default_factory=PriceQuery)


QUERY: dict[str, str] = Query().build()
AVAILABLE_PRICE_ORDERED_QUERY: dict[str, str] = AvailablePriceOrderedQuery().build()
