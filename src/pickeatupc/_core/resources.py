from importlib.resources import files
from importlib.resources.abc import Traversable

from pickeatupc import __package__

_ROOT_PACKAGE: Traversable = files(__package__)
_ASSETS_PACKAGE: Traversable = _ROOT_PACKAGE / "_assets"
CONFIG_FILE_PATH: str = str(_ASSETS_PACKAGE / "config.ini")
