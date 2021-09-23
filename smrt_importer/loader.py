from collections import namedtuple
from datetime import datetime
from enum import Enum
import re


SMRT_FILE_TYPE = 'SMRT'
COMPANY_ID = 'GAZ'
GEN_NUM_FORMAT = re.compile('(PN|DV)[0-9]{6}')


SMRTFileInfo = namedtuple('SMRTFileInfo', 'timestamp gen_num')


class RecordType(Enum):
    header = 'HEADR'


class SMRTLoader:
    def process_header(self, header_fields):
        record_type, file_type, company_id, date_str, time_str, gen_num = header_fields
        
        # TODO: better handling of unexpected values.
        assert record_type == RecordType.header.value
        assert file_type == SMRT_FILE_TYPE
        assert company_id == COMPANY_ID
        assert len(date_str) == 8
        assert len(time_str) == 6
        assert re.fullmatch(GEN_NUM_FORMAT, gen_num) is not None

        timestamp = datetime(
            year=int(date_str[0:4]),
            month=int(date_str[4:6]),
            day=int(date_str[6:8]),
            hour=int(time_str[0:2]),
            minute=int(time_str[2:4]),
            second=int(time_str[4:6])
        )

        return SMRTFileInfo(timestamp, gen_num)