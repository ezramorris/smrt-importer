from collections import namedtuple
from configparser import ConfigParser
from pathlib import Path


_BASE = Path(__file__).parent.parent


class Config:
    """Hold application configuration."""

    def __init__(self):
        self.db_path = None
        self.incoming_dir = None
        self.processed_dir = None
        self.failed_dir = None

    @staticmethod
    def _make_absolute(path):
        if not path.is_absolute():
            path = _BASE / path
        return path

    def load(self):
        """Loads config from config file."""

        config_path = _BASE / 'config.ini'
        parser = ConfigParser()
        parser.read(config_path)

        self.db_path = self._make_absolute(Path(parser['DB']['path']))
        self.incoming_dir = self._make_absolute(Path(parser['Folders']['incoming']))
        self.processed_dir = self._make_absolute(Path(parser['Folders']['processed']))
        self.failed_dir = self._make_absolute(Path(parser['Folders']['failed']))


config = Config()
config.load()
