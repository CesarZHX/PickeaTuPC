from configparser import ConfigParser, SectionProxy

from yarl import URL

from ._resources import CONFIG_FILE_PATH

_CONFIG: ConfigParser = ConfigParser()
_CONFIG.read(CONFIG_FILE_PATH)

_URLS: SectionProxy = _CONFIG["urls"]
SERCOPLUS_URL: URL = URL(_URLS["sercoplus"])

__all__ = ("SERCOPLUS_URL",)
