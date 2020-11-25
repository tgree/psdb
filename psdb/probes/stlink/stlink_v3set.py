# Copyright (c) 2019-2020 by Phase Advanced Sensor Systems, Inc.
import usb
from .stlink_v3_base import STLinkV3_Base


class STLinkV3SET(STLinkV3_Base):
    '''
    STLink V3SET debug probe.  This is a standalone probe available from ST.
    With product ID 0x374F, it is in the mode with a single VCP and MSD.
    '''
    def __init__(self, usb_dev):
        super(STLinkV3SET, self).__init__(usb_dev, 'STLinkV3SET')


def enumerate():
    devices = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0x374F)
    return [STLinkV3SET(d) for d in devices]
