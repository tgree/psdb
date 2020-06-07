# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from . import probe
import psdb


class Probe(probe.Probe):
    def __init__(self, usb_dev, name, usb_reset=False):
        super(Probe, self).__init__(name)
        self.usb_dev = usb_dev
        try:
            self.serial_num = usb_dev.serial_number
        except ValueError as e:
            if str(e) == 'The device has no langid':
                raise psdb.ProbeException('Device has no langid; ensure '
                                          'running as root!')

        self.usb_path = '%s:%s' % (
                self.usb_dev.bus,
                '.'.join('%u' % n for n in self.usb_dev.port_numbers))
        configurations = usb_dev.configurations()
        assert len(configurations) == 1

        if usb_reset:
            usb_dev.reset()

        if (usb_dev.get_active_configuration().bConfigurationValue !=
                configurations[0].bConfigurationValue):
            usb_dev.set_configuration(configurations[0].bConfigurationValue)

    def __str__(self):
        return '%s Debug Probe at %s' % (self.name, self.usb_path)

    def show_info(self):
        print(('============= %s Bus 0x%02X Address 0x%02X %04X:%04X '
               '=============' % (self.name, self.usb_dev.bus,
                                  self.usb_dev.address, self.usb_dev.idVendor,
                                  self.usb_dev.idProduct)))
        print(' Manufacturer: %s' % self.usb_dev.manufacturer)
        print('      Product: %s' % self.usb_dev.product)
        print('Serial Number: %s' % self.usb_dev.serial_number)
        print('     USB Path: %s' % self.usb_path)
