"""SMRT Importer database functionality."""


from sqlalchemy import create_engine, CHAR, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from smrt_importer.config import config


config.db_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
engine = create_engine(f'sqlite+pysqlite:///{config.db_path}')
Session = sessionmaker(engine)
Base = declarative_base()


class File(Base):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    gen_num = Column(CHAR(8), nullable=False)

    records = relationship('Record', back_populates='file')

    def __repr__(self) -> str:
        return f'File(id={self.id!r}, timestamp={self.timestamp!r}, gen_num={self.gen_num!r})'


class Record(Base):
    __tablename__ = 'record'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file.id'), nullable=False)
    meter_number = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    consumption = Column(Float, nullable=True)

    file = relationship('File', back_populates='records')

    def __repr__(self) -> str:
        return f'Record(id={self.id!r}, file_id={self.file_id!r}, ' \
            f'meter_number={self.meter_number!r}, timestamp={self.timestamp!r}, ' \
            f'consumption={self.consumption!r})'


Base.metadata.create_all(engine)
