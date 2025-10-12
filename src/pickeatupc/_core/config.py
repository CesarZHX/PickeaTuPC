from configparser import ConfigParser, SectionProxy

from .resources import CONFIG_FILE_PATH

_CONFIG: ConfigParser = ConfigParser()
_CONFIG.read(CONFIG_FILE_PATH)

URLS: SectionProxy = _CONFIG["urls"]
