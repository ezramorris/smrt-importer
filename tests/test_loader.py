from datetime import datetime
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import TestCase

from smrt_importer.loader import SMRTLoader, DecodingError
from smrt_importer.models import File, Record


VALID_HEADER = ['HEADR', 'SMRT', 'GAZ', '20210102', '135821', 'PN123456']
VALID_CONSUMPTION = ['CONSU', '0000000001', '20201122', '0801', '1.23']
VALID_TRAIL = ['TRAIL']


class ProcessHeaderTestCase(TestCase):
    def test_not_enough_fields(self):
        loader = SMRTLoader()
        header = VALID_HEADER.copy()
        del header[-1]
        with self.assertRaises(DecodingError):
            loader.process_header(header)

    def test_too_many_fields(self):
        loader = SMRTLoader()
        header = VALID_HEADER.copy()
        header.append('foo')
        with self.assertRaises(DecodingError):
            loader.process_header(header)

    def test_invalid_record_type(self):
        loader = SMRTLoader()
        header = VALID_HEADER.copy()
        header[0] = 'FOO'
        with self.assertRaises(DecodingError):
            loader.process_header(header)

    def test_parse_valid_timestamp(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        self.assertEqual(loader.data.timestamp, datetime(2021, 1, 2, 13, 58, 21))

    def test_parse_invalid_date(self):
        loader = SMRTLoader()
        header = VALID_HEADER.copy()
        header[3] = '20211302'
        with self.assertRaises(DecodingError):
            loader.process_header(header)

    def test_parse_invalid_time(self):
        loader = SMRTLoader()
        header = VALID_HEADER.copy()
        header[4] = '605821'
        with self.assertRaises(DecodingError):
            loader.process_header(header)

    def test_parse_valid_gen_num(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        self.assertEqual(loader.data.gen_num, 'PN123456')

    def test_parse_invalid_gen_num(self):
        loader = SMRTLoader()
        header = VALID_HEADER.copy()
        header[5] = 'ABCDEFGH'
        with self.assertRaises(DecodingError):
            loader.process_header(header)


class ProcessConsumptionTestCase(TestCase):
    def test_not_enough_fields(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        values = VALID_CONSUMPTION.copy()
        del values[-1]
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_too_many_fields(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        values = VALID_CONSUMPTION.copy()
        values.append('foo')
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_invalid_record_type(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        values = VALID_CONSUMPTION.copy()
        values[0] = 'FOO'
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_parse_valid_meter_number(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        loader.process_consumption(VALID_CONSUMPTION)
        self.assertEqual(loader.data.records[0].meter_number, '0000000001')

    def test_parse_valid_timestamp(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        loader.process_consumption(VALID_CONSUMPTION)
        self.assertEqual(loader.data.records[0].timestamp, datetime(2020, 11, 22, 8, 1))

    def test_parse_invalid_date(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        values = VALID_CONSUMPTION.copy()
        values[2] = '20210002'
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_parse_invalid_time(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        values = VALID_CONSUMPTION.copy()
        values[3] = '1390'
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_parse_valid_consumption(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        loader.process_consumption(VALID_CONSUMPTION)
        record = loader.data.records[0]
        self.assertEqual(record.consumption, 1.23)
        self.assertIsInstance(record.consumption, float)

    def test_parse_invalid_consumption(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        values = VALID_CONSUMPTION.copy()
        values[4] = 'AAA'
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)


class ProcessTrailTestCase(TestCase):
    def test_parse_valid_trail(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        loader.process_trail(VALID_TRAIL)
        self.assertTrue(loader._received_trail)

    def test_parse_invalid_trail(self):
        loader = SMRTLoader()
        loader.process_header(VALID_HEADER)
        with self.assertRaises(DecodingError):
            loader.process_trail(['FOO'])


class ProcessRecordTestCase(TestCase):
    def test_process_header(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        self.assertIsInstance(loader.data, File)
        self.assertEqual(loader.data.records, [])
        self.assertFalse(loader.is_complete())

    def test_process_header_and_consumption(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        loader.process_record(VALID_CONSUMPTION)
        self.assertEqual(len(loader.data.records), 1)
        self.assertIsInstance(loader.data.records[0], Record)
        self.assertFalse(loader.is_complete())

    def test_process_header_and_trail(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        loader.process_record(VALID_TRAIL)
        self.assertEqual(loader.data.records, [])
        self.assertTrue(loader.is_complete())
    
    def test_process_header_and_consumption_and_trail(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        loader.process_record(VALID_CONSUMPTION)
        loader.process_record(VALID_TRAIL)
        self.assertEqual(len(loader.data.records), 1)
        self.assertTrue(loader.is_complete())

    def test_header_received_after_header(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        with self.assertRaises(DecodingError):
            loader.process_record(VALID_HEADER)

    def test_consumption_received_before_header(self):
        loader = SMRTLoader()
        with self.assertRaises(DecodingError):
            loader.process_record(VALID_CONSUMPTION)

    def test_consumption_received_after_trail(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        loader.process_record(VALID_TRAIL)
        with self.assertRaises(DecodingError):
            loader.process_record(VALID_CONSUMPTION)

    def test_process_invalid_type(self):
        loader = SMRTLoader()
        with self.assertRaises(DecodingError):
            loader.process_record(['FOO', '123', '456'])

class ProcessCSVTestCase(TestCase):
    # No need to test all different scenarios of invalid files as most covered above.
    # Only additional failure scenarios are invalid CSV, and missing trail.

    def test_valid_csv(self):
        # Build CSV into an in-memory file object.
        f = StringIO()
        f.write('"HEADR","SMRT","GAZ","20191011","134942","PN007505"\n')
        f.write('"CONSU","0000000001","20190928","0000",0.00\n')
        f.write('"CONSU","0000000001","20190928","0100",1.52\n')
        f.write('"TRAIL"\n')
        f.seek(0)

        loader = SMRTLoader()
        loader.process_csv(f)
        self.assertEqual(len(loader.data.records), 2)

    def test_no_trail(self):
        # Build CSV into an in-memory file object.
        f = StringIO()
        f.write('"HEADR","SMRT","GAZ","20191011","134942","PN007505"\n')
        f.write('"CONSU","0000000001","20190928","0000",0.00\n')
        f.write('"CONSU","0000000001","20190928","0100",1.52\n')
        f.seek(0)

        loader = SMRTLoader()
        with self.assertRaises(DecodingError):
            loader.process_csv(f)

    def test_invalid_csv(self):
        f = StringIO('"\n')
        f.seek(0)

        loader = SMRTLoader()
        with self.assertRaises(DecodingError):
            loader.process_csv(f)


class ProcessFileTestCase(TestCase):
    def test_process_file(self):
        with TemporaryDirectory() as d:
            p = Path(d) / 'test.csv'
            with open(p, 'w') as f:
                f.write('"HEADR","SMRT","GAZ","20191011","134942","PN007505"\n')
                f.write('"CONSU","0000000001","20190928","0000",0.00\n')
                f.write('"CONSU","0000000001","20190928","0100",1.52\n')
                f.write('"TRAIL"\n')

            loader = SMRTLoader()
            self.assertIs(loader.process_file(p), loader.data)
            self.assertEqual(len(loader.data.records), 2)


if __name__ == '__main__':
    unittest.main()
