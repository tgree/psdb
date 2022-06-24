# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import usb.core

from .. import usb_probe

from .xtswd_095 import XTSWD_095


def enumerate(**kwargs):
    devs = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0xA34E,
                         bDeviceClass=0xFF, bDeviceSubClass=0x03, **kwargs)
    enums = []
    for d in devs:
        cls = XTSWD_095
        enums.append(usb_probe.Enumeration(cls, d))
    return enums
