from collections import namedtuple
from datetime import datetime
from enum import Enum
import re


class Field:
    """Holds information about a CSV field."""

    def __init__(self, name, format=None) -> None:
        """name: field name
        format: regular expression which field values must fully match.
            If None, any value accepted.
        """

        self.name = name
        self.format = format

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, format):
        if format is None:
            self._format = None
        else:
            self._format = re.compile(format)

    def validate(self, value) -> None:
        """Validate a value against this field. Returns if the value is valid,
        otherwise raises a DecodingError.
        """

        if self.format is not None and re.fullmatch(self.format, value) is None:
            raise DecodingError(f'invalid {self.name} value: {value}')


SMRTFileInfo = namedtuple('SMRTFileInfo', 'timestamp gen_num')


class DecodingError(Exception):
    pass


HEADER_FIELDS = [
    Field('record_type', 'HEADR'),
    Field('file_type', 'SMRT'),
    Field('company_id', 'GAZ'),
    Field('date_str', '[0-9]{8}'),
    Field('time_str', '[0-9]{6}'),
    Field('gen_num', '(PN|DV)[0-9]{6}')
]


class SMRTLoader:
    def process_header(self, header_values: list):
        if len(header_values) != len(HEADER_FIELDS):
            raise DecodingError('invalid number of header fields')

        values = {}
        for field, value in zip(HEADER_FIELDS, header_values):
            field.validate(value)
            values[field.name] = value

        date_str, time_str = values['date_str'], values['time_str']

        # It's still possible to fail at this point - we haven't validated
        # the date and time fields represent a valid timestamp.
        try:
            timestamp = datetime(
                year=int(date_str[0:4]),
                month=int(date_str[4:6]),
                day=int(date_str[6:8]),
                hour=int(time_str[0:2]),
                minute=int(time_str[2:4]),
                second=int(time_str[4:6])
            )
        except ValueError as e:
            raise DecodingError(f'failed to parse timestamp: {e}')

        return SMRTFileInfo(timestamp, values['gen_num'])