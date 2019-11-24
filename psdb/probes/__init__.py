# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .xds110 import xds110
from .stlink import stlink_v2_1, stlink_v3e
from .probe import Exception


PROBES = xds110.enumerate() + stlink_v2_1.enumerate() + stlink_v3e.enumerate()


def find_by_serial_number(serial_number):
    p = [p for p in PROBES if p.serial_num == serial_number]
    if not p:
        raise Exception('Serial number "%s" not found.' % serial_number)
    if len(p) > 1:
        raise Exception('Serial number "%s" is ambiguous.' % serial_number)
    return p[0]


def find_by_path(usb_path):
    p = [p for p in PROBES if p.usb_path == usb_path]
    if not p:
        raise Exception('Path "%s" not found.' % usb_path)
    if len(p) > 1:
        raise Exception('Path "%s" is ambiguous.' % usb_path)
    return p[0]


def find_default(serial_number=None, usb_path=None):
    if serial_number:
        return find_by_serial_number(serial_number)
    elif usb_path:
        return find_by_path(usb_path)
    elif PROBES:
        if len(PROBES) == 1:
            return PROBES[0]

        print('Found probes:')
        for p in PROBES:
            p.show_info()
        raise Exception('Multiple probes found.')

    raise Exception('No compatible debug probe found.')
