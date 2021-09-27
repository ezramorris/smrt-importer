"""SMART Importer models."""


from sqlalchemy import CHAR, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class File(Base):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    creation_time = Column(DateTime, nullable=False)
    imported_time = Column(DateTime, nullable=False)
    gen_num = Column(CHAR(8), nullable=False)

    records = relationship('Record', back_populates='file')

    def __repr__(self) -> str:
        return f'File(id={self.id!r}, filename={self.filename!r}, ' \
            f'creation_time={self.creation_time!r}, imported_time={self.imported_time!r}, ' \
            f'gen_num={self.gen_num!r})'


class Record(Base):
    __tablename__ = 'record'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file.id'), nullable=False)
    meter_number = Column(String, nullable=False)
    measurement_time = Column(DateTime, nullable=False)
    consumption = Column(Float, nullable=True)

    file = relationship('File', back_populates='records')

    def __repr__(self) -> str:
        return f'Record(id={self.id!r}, file_id={self.file_id!r}, ' \
            f'meter_number={self.meter_number!r}, timestamp={self.measurement_time!r}, ' \
            f'consumption={self.consumption!r})'
