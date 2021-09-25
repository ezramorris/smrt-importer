from datetime import datetime
import unittest
from unittest import TestCase

from smrt_importer.loader import SMRTLoader, DecodingError, Trail


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
        info = loader.process_header(VALID_HEADER)
        self.assertEqual(info.timestamp, datetime(2021, 1, 2, 13, 58, 21))

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
        info = loader.process_header(VALID_HEADER)
        self.assertEqual(info.gen_num, 'PN123456')

    def test_parse_invalid_gen_num(self):
        loader = SMRTLoader()
        header = VALID_HEADER.copy()
        header[5] = 'ABCDEFGH'
        with self.assertRaises(DecodingError):
            loader.process_header(header)


class ProcessConsumptionTestCase(TestCase):
    def test_not_enough_fields(self):
        loader = SMRTLoader()
        values = VALID_CONSUMPTION.copy()
        del values[-1]
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_too_many_fields(self):
        loader = SMRTLoader()
        values = VALID_CONSUMPTION.copy()
        values.append('foo')
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_invalid_record_type(self):
        loader = SMRTLoader()
        values = VALID_CONSUMPTION.copy()
        values[0] = 'FOO'
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_parse_valid_meter_number(self):
        loader = SMRTLoader()
        record = loader.process_consumption(VALID_CONSUMPTION)
        self.assertEqual(record.meter_number, '0000000001')

    def test_parse_valid_timestamp(self):
        loader = SMRTLoader()
        record = loader.process_consumption(VALID_CONSUMPTION)
        self.assertEqual(record.timestamp, datetime(2020, 11, 22, 8, 1))

    def test_parse_invalid_date(self):
        loader = SMRTLoader()
        values = VALID_CONSUMPTION.copy()
        values[2] = '20210002'
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_parse_invalid_time(self):
        loader = SMRTLoader()
        values = VALID_CONSUMPTION.copy()
        values[3] = '1390'
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)

    def test_parse_valid_consumption(self):
        loader = SMRTLoader()
        record = loader.process_consumption(VALID_CONSUMPTION)
        self.assertEqual(record.consumption, 1.23)
        self.assertIsInstance(record.consumption, float)

    def test_parse_invalid_consumption(self):
        loader = SMRTLoader()
        values = VALID_CONSUMPTION.copy()
        values[4] = 'AAA'
        with self.assertRaises(DecodingError):
            loader.process_consumption(values)


class ProcessTrailTestCase(TestCase):
    def test_parse_valid_trail(self):
        loader = SMRTLoader()
        trail = loader.process_trail(VALID_TRAIL)
        self.assertIsInstance(trail, Trail)

    def test_parse_invalid_trail(self):
        loader = SMRTLoader()
        with self.assertRaises(DecodingError):
            loader.process_trail(['FOO'])

if __name__ == '__main__':
    unittest.main()
