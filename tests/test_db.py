from datetime import datetime
from sqlalchemy import select
from unittest import TestCase
import unittest

from smrt_importer.db import insert_file, Session
from smrt_importer.models import File, Record


class InsertFileTestCase(TestCase):
    def test_insert_file_with_record(self):
        file = File(
            timestamp = datetime.now(),
            gen_num = 'PV123456',
            records = [Record(meter_number='1234', timestamp=datetime.now(), consumption=1.23)]
        )
        file_id = insert_file(file)
        self.assertIsNotNone(file_id)
        with Session() as session:
            try:
                statement = select(File).where(File.id == file_id)
                file, = session.execute(statement).one()
                self.assertEqual(len(file.records), 1)
                self.assertIsNotNone(file.records[0].id)
                for record in file.records:
                    session.delete(record)
            finally:
                session.delete(file)
                session.commit()


if __name__ == '__main__':
    unittest.main()
