from datetime import datetime
import unittest
from unittest import TestCase

from smrt_importer.loader import (
    SMRTLoader, DecodingError, HeaderRecord, ConsumptionRecord
)


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
        self.assertEqual(loader.data.header.timestamp, datetime(2021, 1, 2, 13, 58, 21))

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
        self.assertEqual(loader.data.header.gen_num, 'PN123456')

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
        loader.process_consumption(VALID_CONSUMPTION)
        self.assertEqual(loader.data.consumption_records[0].meter_number, '0000000001')

    def test_parse_valid_timestamp(self):
        loader = SMRTLoader()
        loader.process_consumption(VALID_CONSUMPTION)
        self.assertEqual(loader.data.consumption_records[0].timestamp, datetime(2020, 11, 22, 8, 1))

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
        loader.process_consumption(VALID_CONSUMPTION)
        record = loader.data.consumption_records[0]
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
        loader.process_trail(VALID_TRAIL)
        self.assertTrue(loader.data.received_trail)

    def test_parse_invalid_trail(self):
        loader = SMRTLoader()
        with self.assertRaises(DecodingError):
            loader.process_trail(['FOO'])


class ProcessRecordTestCase(TestCase):
    def test_process_header(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        self.assertTrue(loader.data.has_received_header())
        self.assertIsInstance(loader.data.header, HeaderRecord)
        self.assertEqual(loader.data.consumption_records, [])
        self.assertFalse(loader.data.has_received_trail())

    def test_process_header_and_consumption(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        loader.process_record(VALID_CONSUMPTION)
        self.assertTrue(loader.data.has_received_header())
        self.assertEqual(len(loader.data.consumption_records), 1)
        self.assertIsInstance(loader.data.consumption_records[0], ConsumptionRecord)
        self.assertFalse(loader.data.has_received_trail())

    def test_process_header_and_trail(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        loader.process_record(VALID_TRAIL)
        self.assertTrue(loader.data.has_received_trail())
        self.assertEqual(loader.data.consumption_records, [])
        self.assertTrue(loader.data.has_received_trail())
    
    def test_process_header_and_consumption_and_trail(self):
        loader = SMRTLoader()
        loader.process_record(VALID_HEADER)
        loader.process_record(VALID_CONSUMPTION)
        loader.process_record(VALID_TRAIL)
        self.assertTrue(loader.data.has_received_header())
        self.assertEqual(len(loader.data.consumption_records), 1)
        self.assertTrue(loader.data.has_received_trail())

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


if __name__ == '__main__':
    unittest.main()
