# Copyright (c) 2022-2023 by Phase Advanced Sensor Systems, Inc.
# All rights reserved.
import usb.core
import usb.backend.libusb1
import libusb_package


LIBUSB_BACKEND = None


def get_backend():
    global LIBUSB_BACKEND
    if not LIBUSB_BACKEND:
        LIBUSB_BACKEND = usb.backend.libusb1.get_backend(
                find_library=libusb_package.find_library)
    return LIBUSB_BACKEND


def find(**kwargs):
    return list(usb.core.find(**kwargs, backend=get_backend()))


__all__ = ['find',
           'get_backend',
           ]
