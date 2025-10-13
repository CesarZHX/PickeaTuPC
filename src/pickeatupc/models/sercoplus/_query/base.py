"""Base query module."""

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict


class FrozenQueryConstructor(BaseModel, ABC):
    """Frozen query constructor abstract class."""

    model_config = ConfigDict(frozen=True)

    @abstractmethod
    def build(self) -> dict[str, str]:
        """Build query."""
