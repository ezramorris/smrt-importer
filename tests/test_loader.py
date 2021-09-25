from datetime import datetime
from unittest import TestCase

from smrt_importer.loader import SMRTLoader, DecodingError


VALID_HEADER = ['HEADR', 'SMRT', 'GAZ', '20210102', '135821', 'PN123456']


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
