# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .xds110 import xds110
from .stlink import stlink_v2_1, stlink_v3
from .xtswd import xtswd
from .usb_probe import usb_path
import psdb


def enumerate_probes(**kwargs):
    return (xds110.enumerate(**kwargs) +
            stlink_v2_1.enumerate(**kwargs) +
            stlink_v3.enumerate(**kwargs) +
            xtswd.enumerate(**kwargs))


def dump_probes():
    for e in enumerate_probes():
        e.show_info()


def find_by_serial_number(serial_number):
    def custom_match(usb_dev):
        return usb_dev.serial_num == serial_number
    enumerations = enumerate_probes(custom_match=custom_match)

    if not enumerations:
        raise psdb.ProbeException('Serial number "%s" not found.'
                                  % serial_number)
    if len(enumerations) > 1:
        raise psdb.ProbeException('Serial number "%s" is ambiguous.'
                                  % serial_number)
    return enumerations[0].make_probe()


def find_by_path(_usb_path):
    def custom_match(usb_dev):
        return usb_path(usb_dev) == _usb_path
    enumerations = enumerate_probes(custom_match=custom_match)

    if not enumerations:
        raise psdb.ProbeException('Path "%s" not found.' % usb_path)
    if len(enumerations) > 1:
        raise psdb.ProbeException('Path "%s" is ambiguous.' % usb_path)
    return enumerations[0].make_probe()


def find_default(serial_number=None, usb_path=None):
    if serial_number:
        return find_by_serial_number(serial_number)
    elif usb_path:
        return find_by_path(usb_path)

    enumerations = enumerate_probes()
    if enumerations:
        if len(enumerations) == 1:
            return enumerations[0].make_probe()

        print('Found probes:')
        for e in enumerations:
            e.show_info()
        raise psdb.ProbeException('Multiple probes found.')

    raise psdb.ProbeException('No compatible debug probe found.')
