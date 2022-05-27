# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import usb.core

from . import probe
import psdb


def usb_path(usb_dev):
    return '%s:%s' % (
        usb_dev.bus, '.'.join('%u' % n for n in usb_dev.port_numbers))


class Enumeration(probe.Enumeration):
    def __init__(self, cls, usb_dev):
        super().__init__(cls)
        self.usb_dev = usb_dev

    def make_probe(self):
        return self.cls(self.usb_dev)

    def show_info(self):
        return self.cls.show_info(self.usb_dev)


class Probe(probe.Probe):
    def __init__(self, usb_dev, usb_reset=False):
        super().__init__()
        self.usb_dev = usb_dev
        try:
            self.serial_num = usb_dev.serial_number
        except ValueError as e:
            if str(e) == 'The device has no langid':
                raise psdb.ProbeException('Device has no langid; ensure '
                                          'running as root!')

        configurations = usb_dev.configurations()
        assert len(configurations) == 1

        if usb_reset:
            usb_dev.reset()

        self._set_configuration(configurations[0].bConfigurationValue)

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
