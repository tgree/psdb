# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import usb.core

from .. import usb_probe

from .xtswd_095 import XTSWD_095
from .xtswd_096 import XTSWD_096


def enumerate(**kwargs):
    devs = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0xA34E,
                         bDeviceClass=0xFF, bDeviceSubClass=0x03, **kwargs)
    enums = []
    for d in devs:
        if d.bcdDevice <= 0x095:
            cls = XTSWD_095
        else:
            cls = XTSWD_096
        enums.append(usb_probe.Enumeration(cls, d))
    return enums
