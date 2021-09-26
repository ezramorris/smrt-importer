from collections import namedtuple
from datetime import datetime
from enum import Enum
import re


class FieldType(Enum):
    HEADER = 'HEADR'
    CONSUMPTION = 'CONSU'
    TRAIL = 'TRAIL'


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
ConsumptionRecord = namedtuple('ConsumptionRecord', 'meter_number timestamp consumption')
Trail = namedtuple('Trail', '')


class DecodingError(Exception):
    pass


HEADER_FIELDS = [
    Field('record_type', FieldType.HEADER.value),
    Field('file_type', 'SMRT'),
    Field('company_id', 'GAZ'),
    Field('date_str', '[0-9]{8}'),
    Field('time_str', '[0-9]{6}'),
    Field('gen_num', '(PN|DV)[0-9]{6}')
]


CONSUMPTION_FIELDS = [
    Field('record_type', FieldType.CONSUMPTION.value),
    Field('meter_number'),
    Field('date_str', '[0-9]{8}'),
    Field('time_str', '[0-9]{4}'),
    Field('consumption')
]


TRAIL_FIELDS = [
    Field('record_type', FieldType.TRAIL.value)
]


class SMRTLoader:
    def __init__(self):
        # Lookup table of record processing methods.
        self.methods = {
            FieldType.HEADER: self.process_header,
            FieldType.CONSUMPTION: self.process_consumption,
            FieldType.TRAIL: self.process_trail
        }

    def _process_values(self, fields, values):
        """Validates a list of values and converts them into a dict of
        `{field_name: value}`.

        fields: list of `Field` objects.
        values: list of values to process. Must be the same length as `fields`.
        """

        if len(values) != len(fields):
            raise DecodingError('invalid number of fields')

        items = {}
        for field, value in zip(fields, values):
            field.validate(value)
            items[field.name] = value

        return items

    def _parse_timestamp(self, date_str, time_str):
        """Parse a date and time string into a datetime object.
        
        date_str: 8-digit date string (YYYYMMDD).
        time_str: 6- or 4-digit time string (HHMMSS or HHMM).
        """

        # It's still possible to fail at this point - we haven't validated
        # the date and time fields represent a valid timestamp.
        try:
            timestamp = datetime(
                year=int(date_str[0:4]),
                month=int(date_str[4:6]),
                day=int(date_str[6:8]),
                hour=int(time_str[0:2]),
                minute=int(time_str[2:4]),
                second=int(time_str[4:6] if len(time_str) > 4 else 0)
            )
        except ValueError as e:
            raise DecodingError(f'failed to parse timestamp: {e}')
        
        return timestamp

    def process_header(self, header_values: list):
        """Process a header record.
        
        header_values: list of header record values.
        """

        items = self._process_values(HEADER_FIELDS, header_values)
        timestamp = self._parse_timestamp(items['date_str'], items['time_str'])
        return SMRTFileInfo(timestamp, items['gen_num'])

    def process_consumption(self, consumption_values: list) -> ConsumptionRecord:
        """Process a single consumption record.

        consumption_values: list of consumption record values.
        """

        items = self._process_values(CONSUMPTION_FIELDS, consumption_values)
        timestamp = self._parse_timestamp(items['date_str'], items['time_str'])

        # Cast consumption to float.
        try:
            consumption = float(items['consumption'])
        except ValueError:
            raise DecodingError('failed to parse consumption value')
        
        return ConsumptionRecord(items['meter_number'], timestamp, consumption)
    
    def process_trail(self, trail_values: list) -> Trail:
        """Process a trail record.
        
        trail_values: list of trail record values.
        """

        self._process_values(TRAIL_FIELDS, trail_values)
        return Trail()

    def process_record(self, values):
        """Process a single header, consumption or trail record.
        
        values: list of record values.
        """

        try:
            field_type = FieldType(values[0])
        except ValueError:
            raise DecodingError(f'invalid field type detected: {values[0]}')
        
        method = self.methods[field_type]
        return method(values)
