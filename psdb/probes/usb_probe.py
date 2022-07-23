# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import usb.core

import psdb
from . import probe


def usb_path(usb_dev):
    return '%s:%s' % (
        usb_dev.bus, '.'.join('%u' % n for n in usb_dev.port_numbers))


class Enumeration(probe.Enumeration):
    def __init__(self, cls, usb_dev, *args, **kwargs):
        super().__init__(cls, *args, **kwargs)
        self.usb_dev = usb_dev

    def __repr__(self):
        return self.cls.NAME + ' ' + self.usb_path + ' ' + self.serial_num

    @property
    def serial_num(self):
        return self.usb_dev.serial_number

    @property
    def usb_path(self):
        return usb_path(self.usb_dev)

    def _match_kwargs(self, **kwargs):
        kwargs = super()._match_kwargs(**kwargs)
        if 'serial_num' in kwargs and self.serial_num == kwargs['serial_num']:
            del kwargs['serial_num']
        if 'usb_path' in kwargs and self.usb_path == kwargs['usb_path']:
            del kwargs['usb_path']
        return kwargs

    def make_probe(self):
        return self.cls(self.usb_dev, *self.args, **self.kwargs)

    def show_info(self):
        return self.cls.show_info(self.usb_dev, *self.args, **self.kwargs)


class Probe(probe.Probe):  # pylint: disable=W0223
    def __init__(self, usb_dev, usb_reset=False, bConfigurationValue=None):
        super().__init__()
        self.usb_dev = usb_dev
        try:
            self.serial_num = usb_dev.serial_number
        except ValueError as e:
            if str(e) == 'The device has no langid':
                raise psdb.ProbeException('Device has no langid; ensure '
                                          'running as root!')

        if bConfigurationValue is None:
            configurations = usb_dev.configurations()
            assert len(configurations) == 1
            bConfigurationValue = configurations[0].bConfigurationValue

        if usb_reset:
            usb_dev.reset()

        self._set_configuration(bConfigurationValue)

    def __str__(self):
        return '%s Debug Probe at %s' % (self.NAME, usb_path(self.usb_dev))

    def _get_active_configuration(self):
        try:
            return self.usb_dev.get_active_configuration()
        except usb.core.USBError as e:
            if e.strerror != 'Configuration not set':
                raise
        return None

    def _set_configuration(self, bConfigurationValue, force=False):
        cfg = self._get_active_configuration()
        if (cfg is None or cfg.bConfigurationValue != bConfigurationValue or
                force):
            usb.util.dispose_resources(self.usb_dev)
            self.usb_dev.set_configuration(bConfigurationValue)

    @classmethod
    def show_info(cls, usb_dev):
        print(('============= %s Bus 0x%02X Address 0x%02X %04X:%04X '
               '=============' % (cls.NAME, usb_dev.bus,
                                  usb_dev.address, usb_dev.idVendor,
                                  usb_dev.idProduct)))
        print(' Manufacturer: %s' % usb_dev.manufacturer)
        print('      Product: %s' % usb_dev.product)
        print('Serial Number: %s' % usb_dev.serial_number)
        print('     USB Path: %s' % usb_path(usb_dev))
