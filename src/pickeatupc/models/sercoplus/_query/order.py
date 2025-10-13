"""Order query module."""

from enum import StrEnum

from pydantic import Field

from .base import FrozenQueryConstructor


class OrderBy(StrEnum):
    """Order by enum."""

    SALES = "sales"
    POSITION = "position"
    NAME = "name"
    PRICE = "price"
    REFERENCE = "reference"


class OrderQuery(FrozenQueryConstructor):
    """Order query model."""

    order_by: OrderBy | None = Field(default=None)
    desc: bool = Field(default=False)

    def build(self) -> dict[str, str]:
        """Build query. Order by property defaults to position."""
        if not self.order_by:
            return dict()
        order: str = "desc" if self.desc else "asc"
        return dict(order=f"product.{self.order_by}.{order}")


class PriceQuery(OrderQuery):
    """Price query model."""

    order_by: OrderBy | None = Field(default=OrderBy.PRICE)
