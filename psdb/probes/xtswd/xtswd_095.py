# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
from .xtswd import XTSWD, Response


CMD_EP  = 0x01
RSP_EP  = 0x82
IMON_EP = 0x83


class XTSWD_095(XTSWD):
    def __init__(self, usb_dev):
        super().__init__(usb_dev, CMD_EP, RSP_EP, IMON_EP, usb_reset=True)

    def _decode_rsp(self, data):
        rsp     = Response.unpack(data[:Response._STRUCT.size])
        rx_data = bytes(data[Response._STRUCT.size:])
        return rsp, rx_data
