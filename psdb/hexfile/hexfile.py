# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.


class HEXFileException(Exception):
    pass


class InvalidFormatException(HEXFileException):
    pass


class HEXFile(object):
    def __init__(self, path):
        self.path     = path
        self.hex_file = open(self.path, 'r')
        self.flash_dv = []

        self._parse()

    def _raise_inval_format(self, i, err):
        raise InvalidFormatException('%s:%u: %s' % (self.path, i, err))

    def _parse(self):
        base_address = 0
        try:
            lines = self.hex_file.readlines()
        except UnicodeDecodeError:
            self._raise_inval_format(0, 'Non-UTF8 characters.')
        for i, l in enumerate(lines):
            l = l.strip()
            if l[0] != ':':
                self._raise_inval_format(i, 'Expected ":".')
            if len(l) < 11:
                self._raise_inval_format(i, 'Line too short.')
            l = l[1:]
            if len(l) % 2:
                self._raise_inval_format(i, 'Odd record length.')
            record_hex  = [int(l[i:i+2], 16) for i in range(0, len(l), 2)]
            byte_count  = record_hex[0]
            offset      = (record_hex[1] << 8) | record_hex[2]
            record_type = record_hex[3]
            data        = bytes(record_hex[4:-1])
            if (sum(record_hex) & 0xFF):
                self._raise_inval_format(i, 'Invalid checksum.')

            if record_type == 0x00:
                self.flash_dv.append((base_address + offset, data))
            elif record_type == 0x01:
                break
            elif record_type == 0x02:
                if byte_count != 2:
                    self._raise_inval_format(i, 'Invalid type 2 record.')
                base_address = ((data[0] << 8) | data[1])*16
            elif record_type == 0x03:
                if byte_count != 4:
                    self._raise_inval_format(i, 'Invalid type 3 record.')
                self.ss_cs = ((data[0] << 8) | data[1])
                self.ss_ip = ((data[2] << 8) | data[3])
            elif record_type == 0x04:
                if byte_count != 2:
                    self._raise_inval_format(i, 'Invalid type 4 record.')
                base_address = ((data[0] << 24) | (data[1] << 16))
            elif record_type == 0x05:
                if byte_count != 4:
                    self._raise_inval_format(i, 'Invalid type 5 record.')
                self.sla_eip = ((data[0] << 24) |
                                (data[1] << 16) |
                                (data[2] <<  8) |
                                (data[3] <<  0))
            else:
                self._raise_inval_format(i, 'Unrecognied type %u record.'
                                         % record_type)
