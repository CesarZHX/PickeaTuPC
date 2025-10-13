"""Page number model."""

from pydantic import PositiveInt, RootModel


class PageNumber(RootModel):
    """Page number model."""

    root: PositiveInt

    def __str__(self) -> str:
        """Get page number."""
        return str(self.root)

    def __int__(self) -> int:
        """Get page number."""
        return int(self.root)

    @classmethod
    def minimun(cls) -> "PageNumber":
        """Get minimum page number."""
        return cls(root=1)

    def is_minimun(self) -> bool:
        """Check if page number is minimum."""
        minimun: PageNumber = self.minimun()
        return self == minimun
