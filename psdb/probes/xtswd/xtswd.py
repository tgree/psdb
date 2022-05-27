# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
from enum import IntEnum
import random
import usb.core
import usb.util

from .. import usb_probe
import psdb

import btype


TX_EP = 0x01
RX_EP = 0x82

TRACE_EN   = False
FREQ_LIMIT = None


def trace(msg):
    if TRACE_EN:
        print(msg)


class Status(IntEnum):
    OK              = 0
    BAD_OPCODE      = 1
    FREQ_TOO_LOW    = 2
    SWD_ACK_ERR     = 3
    SWD_PARITY_ERR  = 4
    BAD_LENGTH      = 5
    BAD_WORD_SIZE   = 6
    MISALIGNED_ADDR = 7
    PAGE_OVERFLOW   = 8
    BAD_CMD_LENGTH  = 9

    @staticmethod
    def rsp_to_status_str(rsp):
        try:
            s = '%s' % Status(rsp.status)
        except ValueError:
            s = '%u' % rsp.status
        return s


class Opcode(IntEnum):
    SET_FREQ   = 0x01
    CONNECT    = 0x02
    SET_SRST   = 0x03
    READ_DP    = 0x10
    WRITE_DP   = 0x11
    READ_AP    = 0x20
    WRITE_AP   = 0x21
    READ8      = 0x30
    WRITE8     = 0x31
    READ16     = 0x32
    WRITE16    = 0x33
    READ32     = 0x34
    WRITE32    = 0x35
    BULK_READ  = 0x36
    BULK_WRITE = 0x37


class Command(btype.Struct):
    opcode         = btype.uint16_t()
    tag            = btype.uint16_t()
    params         = btype.Array(btype.uint32_t(), 7)
    _EXPECTED_SIZE = 32


class Response(btype.Struct):
    opcode         = btype.uint16_t()
    tag            = btype.uint16_t()
    status         = btype.uint32_t()
    params         = btype.Array(btype.uint32_t(), 6)
    _EXPECTED_SIZE = 32


class XTSWDCommandException(psdb.ProbeException):
    def __init__(self, rsp, rx_data):
        super().__init__(
            'Command exception: %s (%s)' % (Status.rsp_to_status_str(rsp), rsp))
        self.rsp = rsp
        self.rx_data = rx_data


class XTSWD(usb_probe.Probe):
    NAME = 'XTSWD'

    def __init__(self, usb_dev):
        super().__init__(usb_dev, usb_reset=True)
        self.tag = random.randint(0, 65535)
        self.git_sha1 = usb.util.get_string(usb_dev, 6)

    def _exec_command(self, opcode, params=None, bulk_data=b'', timeout=1000,
                      rx_len=0):
        if not params:
            params = [0, 0, 0, 0, 0, 0, 0]
        elif len(params) < 7:
            params = params + [0]*(7 - len(params))

        tag      = self.tag
        self.tag = (self.tag + 1) & 0xFFFF

        cmd  = Command(opcode=opcode, tag=tag, params=params)
        data = cmd.pack()
        self.usb_dev.write(TX_EP, data + bulk_data, timeout=timeout)

        data = self.usb_dev.read(RX_EP, Response._STRUCT.size + rx_len,
                                 timeout=timeout)
        assert len(data) >= Response._STRUCT.size
        rsp = Response.unpack(data[:Response._STRUCT.size])
        assert rsp.tag == tag

        rx_data = bytes(data[Response._STRUCT.size:])
        if rsp.status != Status.OK:
            raise XTSWDCommandException(rsp, rx_data)

        assert len(rx_data) == rx_len
        return rsp, rx_data

    def _bulk_read(self, addr, n, word_size, ap_num=0):
        trace('BULK READ%u: 0x%08X len %u' % (word_size, addr, n*word_size))
        _, data = self._exec_command(Opcode.BULK_READ,
                                     [ap_num, addr, n, word_size],
                                     rx_len=n*word_size)
        return data

    def _bulk_read_8(self, addr, n, ap_num=0):
        return self._bulk_read(addr, n, 1, ap_num=ap_num)

    def _bulk_read_16(self, addr, n, ap_num=0):
        return self._bulk_read(addr, n, 2, ap_num=ap_num)

    def _bulk_read_32(self, addr, n, ap_num=0):
        return self._bulk_read(addr, n, 4, ap_num=ap_num)

    def _bulk_write(self, data, addr, word_size, ap_num=0):
        trace('BULK WRITE%u: 0x%08X len %u' % (word_size, addr, len(data)))
        assert len(data) % word_size == 0
        n = len(data) // word_size
        self._exec_command(Opcode.BULK_WRITE, [ap_num, addr, n, word_size],
                           bulk_data=data)

    def _bulk_write_8(self, data, addr, ap_num=0):
        self._bulk_write(data, addr, 1, ap_num=ap_num)

    def _bulk_write_16(self, data, addr, ap_num=0):
        self._bulk_write(data, addr, 2, ap_num=ap_num)

    def _bulk_write_32(self, data, addr, ap_num=0):
        self._bulk_write(data, addr, 4, ap_num=ap_num)

    def assert_srst(self):
        self._exec_command(Opcode.SET_SRST, [1])

    def deassert_srst(self):
        self._exec_command(Opcode.SET_SRST, [0])

    def set_tck_freq(self, freq):
        # Artifically limit frequency to 1 MHz due to Rhino bite issues.
        if FREQ_LIMIT is not None:
            freq = min(freq, FREQ_LIMIT)
        rsp, _ = self._exec_command(Opcode.SET_FREQ, [freq])
        return rsp.params[0]

    def open_ap(self, apsel):
        pass

    def read_dp_reg(self, addr):
        rsp, _ = self._exec_command(Opcode.READ_DP, [addr])
        return rsp.params[0]

    def write_dp_reg(self, addr, value):
        self._exec_command(Opcode.WRITE_DP, [addr, value])

    def read_ap_reg(self, apsel, addr):
        rsp, _ = self._exec_command(Opcode.READ_AP, [apsel, addr])
        return rsp.params[0]

    def write_ap_reg(self, apsel, addr, value):
        self._exec_command(Opcode.WRITE_AP, [apsel, addr, value])

    def read_32(self, addr, ap_num=0):
        trace('READ32 0x%08X' % addr)
        rsp, _ = self._exec_command(Opcode.READ32, [ap_num, addr])
        trace('...0x%08X' % rsp.params[0])
        return rsp.params[0]

    def read_16(self, addr, ap_num=0):
        trace('READ16 0x%08X' % addr)
        rsp, _ = self._exec_command(Opcode.READ16, [ap_num, addr])
        trace('...0x%04X' % rsp.params[0])
        return rsp.params[0]

    def read_8(self, addr, ap_num=0):
        trace('READ8 0x%08X' % addr)
        rsp, _ = self._exec_command(Opcode.READ8, [ap_num, addr])
        trace('...0x%02X' % rsp.params[0])
        return rsp.params[0]

    def write_32(self, v, addr, ap_num=0):
        trace('WRITE32 0x%08X <- 0x%08X' % (addr, v))
        self._exec_command(Opcode.WRITE32, [ap_num, addr, v])

    def write_16(self, v, addr, ap_num=0):
        trace('WRITE16 0x%08X <- 0x%04X' % (addr, v))
        self._exec_command(Opcode.WRITE16, [ap_num, addr, v])

    def write_8(self, v, addr, ap_num=0):
        trace('WRITE8 0x%08X <- 0x%02X' % (addr, v))
        self._exec_command(Opcode.WRITE8, [ap_num, addr, v])

    def connect(self):
        rsp, _ = self._exec_command(Opcode.CONNECT)
        self.dpidr = rsp.params[0]
        trace('DPIDR:     0x%08X' % self.dpidr)
        trace('CTRL/STAT: 0x%08X' % rsp.params[1])
        trace('CSW:       0x%08X' % self.read_ap_reg(0, 0x0))

    @staticmethod
    def show_fw_version(usb_dev):
        v = usb_dev.bcdDevice
        print(' Firmware Ver: %u.%u.%u' % ((v >> 8) & 0xF,
                                           (v >> 4) & 0xF,
                                           (v >> 0) & 0xF))

    @classmethod
    def show_info(cls, usb_dev):
        super().show_info(usb_dev)
        XTSWD.show_fw_version(usb_dev)

    def show_detailed_info(self):
        super().show_info(self.usb_dev)
        print('         SHA1: %s' % self.git_sha1)
        self.show_fw_version(self.usb_dev)


def enumerate(**kwargs):
    return [usb_probe.Enumeration(XTSWD, usb_dev)
            for usb_dev in usb.core.find(find_all=True, idVendor=0x0483,
                                         idProduct=0xA34E, bDeviceClass=0xFF,
                                         bDeviceSubClass=0x03, **kwargs)]
