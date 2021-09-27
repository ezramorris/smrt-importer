from datetime import datetime
import unittest
from unittest import TestCase
from unittest.mock import Mock, patch

from smrt_importer.loader import SMRTLoader
from smrt_importer.models import File
from smrt_importer.processor import process_file


class ProcessFileTestCase(TestCase):
    @patch('smrt_importer.processor.insert_file')
    def test_process_file(self, mock_insert_file):
        file = File(timestamp=datetime.now(), gen_num='PV123456')
        SMRTLoader.load_file = Mock(return_value=file)
        process_file('foo')
        mock_insert_file.assert_called_once_with(file)


if __name__ == '__main__':
    unittest.main()
