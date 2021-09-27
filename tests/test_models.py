from datetime import datetime
from sqlalchemy import select
import unittest
from unittest import TestCase

from smrt_importer.db import Session
from smrt_importer.models import File, Record


class FileTestCase(TestCase):
    def test_crd_file(self):
        filename = 'FOO.SMRT'
        creation_time = datetime(2020, 1, 2, 3, 4, 5)
        imported_time = datetime(2021, 10, 3, 2, 1)
        gen_num = 'AA123456'
        with Session() as session:
            # Create and commit.
            file = File(
                filename=filename,
                creation_time=creation_time,
                imported_time=imported_time,
                gen_num=gen_num
            )
            session.add(file)
            session.commit()

            try:
                file_id = file.id

                # Query DB based on ID and check.
                statement = select(File).where(File.id == file_id)
                file, = session.execute(statement).one()
                self.assertEqual(file.filename, filename)
                self.assertEqual(file.creation_time, creation_time)
                self.assertEqual(file.imported_time, imported_time)
                self.assertEqual(file.gen_num, gen_num)

            finally:
                # Delete file.
                session.delete(file)
                session.commit()


class RecordTestCase(TestCase):
    def test_crd_record(self):
        filename = 'FOO.SMRT'
        creation_time = datetime(2020, 1, 2, 3, 4, 5)
        imported_time = datetime(2021, 10, 3, 2, 1)
        gen_num = 'AA123456'
        measurement_time = datetime(2020, 1, 2, 0, 0)
        meter_number = 'dummy meter number'
        consumption = 1.23
        with Session() as session:
            # Create and commit.
            file = File(
                filename=filename,
                creation_time=creation_time,
                imported_time=imported_time,
                gen_num=gen_num
            )
            record = Record(
                file=file, 
                meter_number=meter_number, 
                measurement_time=measurement_time, 
                consumption=consumption
            )
            session.add(file)
            session.add(record)
            session.commit()

            try:
                record_id = record.id

                # Query DB based on ID and check.
                statement = select(Record).where(Record.id == record_id)
                record, = session.execute(statement).one()
                self.assertEqual(record.file.id, file.id)
                self.assertEqual(record.measurement_time, measurement_time)
                self.assertEqual(record.meter_number, meter_number)
                self.assertEqual(record.consumption, consumption)

            finally:
                # Delete file.
                session.delete(record)
                session.delete(file)
                session.commit()

if __name__ == '__main__':
    unittest.main()
