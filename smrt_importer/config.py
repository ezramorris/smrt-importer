from collections import namedtuple
from configparser import ConfigParser
from pathlib import Path


Config = namedtuple('Config', 'db_path')


def load_config():
    """Loads config from config file and returns a Config object."""

    base = config_path = Path(__file__).parent.parent
    config_path = base / 'config.ini'
    parser = ConfigParser()
    parser.read(config_path)

    db_path = Path(parser['DB']['path'])
    if not db_path.is_absolute():
        db_path = base / db_path

    return Config(db_path)


config = load_config()
