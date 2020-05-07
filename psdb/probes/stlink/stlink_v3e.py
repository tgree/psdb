# Copyright (c) 2019-2020 by Phase Advanced Sensor Systems, Inc.
import usb
from .stlink_v3_base import STLinkV3_Base


class STLinkV3E(STLinkV3_Base):
    '''
    STLink V3E debug probe.  This can be found on the Nucleo 64 board we have
    for the STM32G475 chip.
    '''
    def __init__(self, usb_dev):
        super(STLinkV3E, self).__init__(usb_dev, 'STLinkV3E')


def enumerate():
    devices = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0x374E)
    return [STLinkV3E(d) for d in devices]
