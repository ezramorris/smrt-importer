"""SMRT Importer database functionality."""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smrt_importer.config import config
from smrt_importer.models import Base, File


config.db_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
engine = create_engine(f'sqlite+pysqlite:///{config.db_path}')
Session = sessionmaker(engine)

Base.metadata.create_all(engine)


def insert_file(file: File):
    """Inserts a file (potentially containing records) into the DB.
    
    Returns the ID of the newly inserted row.
    """

    with Session() as session:
        session.add(file)
        session.commit()
        file_id = file.id

    return file_id
