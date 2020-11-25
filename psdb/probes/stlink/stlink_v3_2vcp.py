# Copyright (c) 2019-2020 by Phase Advanced Sensor Systems, Inc.
import usb
from .stlink_v3_base import STLinkV3_Base


class STLinkV3_2VCP(STLinkV3_Base):
    '''
    When I updated my STLINK-V3SET to disable MSD mode and have 2 VCP links
    instead, the PID changed to 0x3753.  It also self-identifies on USB as an
    "STLINK-V3" instead of "STLINK-V3SET".  In the OpenOCD sources, this PID is
    labeled "STLINK_V3_2VCP_PID" and the original V3SET PID is labelled as
    "STLINK_V3S_PID".  When I revert the V3SET to re-enable MSD mode, the PID
    changes back to the original value but it still self-identifies on USB as
    an "STLINK-V3".  Maybe it always did - unfortunately I don't have a USB
    capture that predates this change.
    '''
    def __init__(self, usb_dev):
        super(STLinkV3_2VCP, self).__init__(usb_dev, 'STLinkV3_2VCP')


def enumerate():
    devices = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0x3753)
    return [STLinkV3_2VCP(d) for d in devices]
