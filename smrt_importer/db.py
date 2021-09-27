"""SMRT Importer database functionality."""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smrt_importer.config import config
from smrt_importer.models import Base


config.db_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
engine = create_engine(f'sqlite+pysqlite:///{config.db_path}')
Session = sessionmaker(engine)

Base.metadata.create_all(engine)
