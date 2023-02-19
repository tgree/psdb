# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
from enum import IntEnum
import random
import usb.core
import usb.util

import btype

import psdb
from .. import usb_probe


TRACE_EN   = False


# Approximate ADC-to-mA ratio for prototype board.
MA_RATIO = 11.047


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
    ALREADY         = 10
    DATA_OVERRUN    = 11
    DATA_UNDERRUN   = 12
    ABORTED         = 13

    @staticmethod
    def rsp_to_status_str(rsp):
        try:
            s = '%s' % Status(rsp.status)
        except ValueError:
            s = '%u' % rsp.status
        return s


class Opcode(IntEnum):
    SET_FREQ    = 0x01
    CONNECT     = 0x02
    SET_SRST    = 0x03
    ENABLE_INA  = 0x04
    DISABLE_INA = 0x05
    START_IMON  = 0x06
    STOP_IMON   = 0x07
    GET_STATS   = 0x08
    READ_DP     = 0x10
    WRITE_DP    = 0x11
    READ_AP     = 0x20
    WRITE_AP    = 0x21
    READ8       = 0x30
    WRITE8      = 0x31
    READ16      = 0x32
    WRITE16     = 0x33
    READ32      = 0x34
    WRITE32     = 0x35
    BULK_READ   = 0x36
    BULK_WRITE  = 0x37
    BAD_OPCODE  = 0xCCCC


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


class IMonData(btype.Struct):
    tag             = btype.uint16_t()
    oversample_log2 = btype.uint8_t()
    rsrv            = btype.uint8_t()
    seq             = btype.uint32_t()
    freq_num        = btype.uint32_t()
    freq_denom      = btype.uint32_t()
    samples         = btype.Array(btype.uint16_t(), 10000)
    _EXPECTED_SIZE  = 20016


class Stats:
    def __init__(self, rsp):
        self.nreads       = rsp.params[0]
        self.nread_waits  = rsp.params[1]
        self.nwrites      = rsp.params[2]
        self.nwrite_waits = rsp.params[3]

    def dump(self):
        print('      nreads: %u' % self.nreads)
        print(' nread_waits: %u' % self.nread_waits)
        print('     nwrites: %u' % self.nwrites)
        print('nwrite_waits: %u' % self.nwrite_waits)


class XTSWDCommandException(psdb.ProbeException):
    def __init__(self, rsp, rx_data):
        super().__init__(
            'Command exception: %s (%s)' % (Status.rsp_to_status_str(rsp), rsp))
        self.rsp = rsp
        self.rx_data = rx_data


class XTSWD(usb_probe.Probe):
    NAME    = 'XTSWD'
    RSP_EP  = 0x81
    CMD_EP  = 0x02
    IMON_EP = 0x83

    def __init__(self, usb_dev, **kwargs):
        super().__init__(usb_dev, bConfigurationValue=0x30, **kwargs)
        self.tag         = random.randint(0, 65535)
        self.imon_tag    = None
        self.git_sha1    = usb.util.get_string(usb_dev, 6)
        self.njunk_bytes = self._synchronize()

        # Stop current monitoring in case it had been started previously.
        self.stop_current_monitoring()

    def _synchronize(self):
        '''
        Recover the connection if it was interrupted previously.  There could
        be a bunch of data posted on the RSP EP from a previous lifetime, so
        we post illegal commands to the probe until we get a 32-byte response.
        However, that 32-byte response could be the end of the previous life's
        transfer, so do a final illegal command and then check for the expected
        opcode and tag.
        '''
        self._send_abort()
        tag  = self._alloc_tag()
        cmd  = Command(opcode=Opcode.BAD_OPCODE, tag=tag)
        data = cmd.pack()
        junk = 0
        while True:
            self.usb_dev.write(self.CMD_EP, data)
            rsp = self.usb_dev.read(self.RSP_EP, 64)
            if len(rsp) == 32:
                break

            junk += len(rsp)

        self.usb_dev.write(self.CMD_EP, data)
        data = self.usb_dev.read(self.RSP_EP, 64)
        assert len(data) == 32

        rsp = Response.unpack(data)
        assert rsp.tag    == tag
        assert rsp.opcode == Opcode.BAD_OPCODE
        assert rsp.status == Status.BAD_OPCODE

        return junk

    def _send_abort(self):
        self.usb_dev.write(self.CMD_EP, b'')

    def _alloc_tag(self):
        tag      = self.tag
        self.tag = (self.tag + 1) & 0xFFFF
        return tag

    def _exec_command(self, opcode, params=None, bulk_data=b'', timeout=1000,
                      rx_len=0):
        if not params:
            params = [0, 0, 0, 0, 0, 0, 0]
        elif len(params) < 7:
            params = params + [0]*(7 - len(params))

        tag  = self._alloc_tag()
        cmd  = Command(opcode=opcode, tag=tag, params=params)
        data = cmd.pack()
        size = self.usb_dev.write(self.CMD_EP, data + bulk_data,
                                  timeout=timeout)
        assert size == len(data) + len(bulk_data)

        data = self.usb_dev.read(self.RSP_EP, Response._STRUCT.size + rx_len,
                                 timeout=timeout)
        assert len(data) >= Response._STRUCT.size

        rsp = Response.unpack(
                data[-Response._STRUCT.size:])          # pylint: disable=E1130
        rx_data = bytes(data[:-Response._STRUCT.size])  # pylint: disable=E1130
        assert rsp.tag == tag

        if rsp.status != Status.OK:
            rsp.opcode = Opcode(rsp.opcode)
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

    def _set_tck_freq(self, freq_hz):
        rsp, _ = self._exec_command(Opcode.SET_FREQ, [freq_hz])
        return rsp.params[0]

    def enable_instrumentation_amp(self):
        self._exec_command(Opcode.ENABLE_INA)

    def disable_instrumentation_amp(self):
        self._exec_command(Opcode.DISABLE_INA)

    def start_current_monitoring(self):
        rsp, _ = self._exec_command(Opcode.START_IMON)
        self.imon_tag = rsp.tag

    def stop_current_monitoring(self):
        self._exec_command(Opcode.STOP_IMON)

    def read_current_monitor_data(self):
        while True:
            data = self.usb_dev.read(self.IMON_EP, IMonData._STRUCT.size,
                                     timeout=1000)
            idata = IMonData.unpack(data)
            if idata.tag == self.imon_tag:
                return idata, data[-20000:]

    def read_current_consumption(self):
        while True:
            data = self.usb_dev.read(self.IMON_EP, IMonData._STRUCT.size,
                                     timeout=1000)
            idata = IMonData.unpack(data)
            if idata.tag == self.imon_tag:
                break

        ovr  = (1 << idata.oversample_log2)
        vals = [v / ovr for v in idata.samples]
        vals = [v / MA_RATIO for v in vals]
        return sum(vals) / len(vals)

    def get_stats(self):
        rsp, _ = self._exec_command(Opcode.GET_STATS)
        return Stats(rsp)

    def open_ap(self, ap_num):
        pass

    def read_dp_reg(self, addr):
        rsp, _ = self._exec_command(Opcode.READ_DP, [addr])
        return rsp.params[0]

    def write_dp_reg(self, addr, value):
        self._exec_command(Opcode.WRITE_DP, [addr, value])

    def read_ap_reg(self, ap_num, addr):
        rsp, _ = self._exec_command(Opcode.READ_AP, [ap_num, addr])
        return rsp.params[0]

    def write_ap_reg(self, ap_num, addr, value):
        self._exec_command(Opcode.WRITE_AP, [ap_num, addr, value])

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
        dpidr  = rsp.params[0]
        trace('DPIDR:     0x%08X' % dpidr)
        trace('CTRL/STAT: 0x%08X' % rsp.params[1])
        trace('CSW:       0x%08X' % self.read_ap_reg(0, 0x0))
        return dpidr

    @staticmethod
    def find():
        devs = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0xA34E,
                             bDeviceClass=0xFF, bDeviceSubClass=0x03)
        return [usb_probe.Enumeration(XTSWD, d) for d in devs]

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
