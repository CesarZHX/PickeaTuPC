"""Availability query module."""

from pydantic import Field

from .base import FrozenQueryConstructor


class AvailabilityQuery(FrozenQueryConstructor):
    """Availability query model."""

    in_stock: bool = Field(default=False)
    not_available: bool = Field(default=False)

    def build(self) -> dict[str, str]:
        """Build query. All properties are default to True."""
        if not (self.in_stock or self.not_available):
            return dict()
        parts: list[str] = ["Disponibilidad"]
        if self.in_stock:
            parts.append("En stock")
        if self.not_available:
            parts.append("No disponible")
        return dict(q="-".join(parts))


class AvailableQuery(AvailabilityQuery):
    """Available query model."""

    in_stock: bool = Field(default=True)
