from datetime import datetime
from unittest import TestCase

from smrt_importer.loader import SMRTLoader


VALID_HEADER = ['HEADR', 'SMRT', 'GAZ', '20210102', '135821', 'PN123456']


class ProcessHeaderTestCase(TestCase):
    def test_parse_valid_timestamp(self):
        loader = SMRTLoader()
        info = loader.process_header(VALID_HEADER)
        self.assertEqual(info.timestamp, datetime(2021, 1, 2, 13, 58, 21))

    def test_parse_valid_gen_num(self):
        loader = SMRTLoader()
        info = loader.process_header(VALID_HEADER)
        self.assertEqual(info.gen_num, 'PN123456')
