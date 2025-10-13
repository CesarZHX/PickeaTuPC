"""Query module."""

from pydantic import Field

from .availability import AvailabilityQuery, AvailableQuery
from .base import FrozenQueryConstructor
from .order import OrderQuery, PriceQuery


class Query(FrozenQueryConstructor):
    """Query model."""

    availability: AvailabilityQuery = Field(default_factory=AvailabilityQuery)
    order: OrderQuery = Field(default_factory=OrderQuery)

    def build(self) -> dict[str, str]:
        """Build query."""
        return self.availability.build() | self.order.build()


class AvailablePriceOrderedQuery(Query):
    """Available price ordered query model."""

    availability: AvailabilityQuery = Field(default_factory=AvailableQuery)
    order: OrderQuery = Field(default_factory=PriceQuery)


QUERY: dict[str, str] = Query().build()
AVAILABLE_PRICE_ORDERED_QUERY: dict[str, str] = AvailablePriceOrderedQuery().build()
