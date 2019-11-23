# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import usb
from . import usb_probe
import psdb

from struct import pack, unpack, unpack_from
from builtins import bytes, range
import time


RX_EP    = 0x81
TX_EP    = 0x01

DATA_SIZE = 4096

MODE_EXIT_CMD = {0x00: bytes(b'\xF3\x07'), # DFU
                 0x02: bytes(b'\xF2\x21'), # DEBUG
                 0x03: bytes(b'\xF4\x01'), # SWIM
                 }

FEATURE_RW_STATUS_12  = (1 << 0)
FEATURE_SWD_SET_FREQ  = (1 << 1)
FEATURE_BULK_READ_16  = (1 << 2)
FEATURE_BULK_WRITE_16 = (1 << 3)


class STLink(usb_probe.Probe):
    '''
    STLink V2.1 debug probe.  This can be found on the Nucleo 144 board we have
    for the STM32H7xx chip.  The USART3 device from the MCU is connected to the
    debug probe as a virtual COM port.
    '''
    def __init__(self, usb_dev, name):
        super(STLink, self).__init__(usb_dev, name)
        self.dpidr    = None
        self.features = 0

    def _usb_xfer_in(self, cmd, size):
        cmd = cmd + bytes(b'\x00'*(16 - len(cmd)))
        assert len(cmd) == 16
        assert self.usb_dev.write(TX_EP, cmd) == len(cmd)
        if size is None:
            return self.usb_dev.read(RX_EP, DATA_SIZE, timeout=1000)
        rsp = self.usb_dev.read(RX_EP, size, timeout=1000)
        assert len(rsp) == size
        return rsp

    def _usb_last_xfer_status(self):
        return self._usb_xfer_in(bytes(b'\xF2\x3E'), 12)

    def _usb_xfer_out(self, cmd, data):
        cmd = cmd + bytes(b'\x00'*(16 - len(cmd)))
        assert len(cmd) == 16
        assert self.usb_dev.write(TX_EP, cmd) == len(cmd)
        assert self.usb_dev.write(TX_EP, data, timeout=1000) == len(data)
        assert self._usb_last_xfer_status()[0] == 0x80

    def _usb_xfer_null(self, cmd):
        cmd = cmd + bytes(b'\x00'*(16 - len(cmd)))
        assert len(cmd) == 16
        assert self.usb_dev.write(TX_EP, cmd) == len(cmd)

    def _cmd_allow_retry(self, cmd, size):
        for _ in range(10):
            data = self._usb_xfer_in(cmd, size)
            if data[0] == 0x80:
                return data

            if data[0] not in (0x10, 0x14):
                raise Exception('Unexpected error 0x%02X: %s' % (data[0], data))
            time.sleep(0.1)
        raise Exception('Max retries exceeded!')

    def _usb_version(self):
        rsp = self._usb_xfer_in(bytes(b'\xF1'), 6)
        v0, v1, vid, pid = unpack('<BBHH', rsp)
        v = (v0 << 8) | v1
        self.ver_stlink = (v >> 12) & 0x0F
        self.ver_jtag   = (v >>  6) & 0x3F
        self.ver_swim   = (v >>  0) & 0x3F
        self.ver_vid    = vid
        self.ver_pid    = pid

    def _read_dpidr(self):
        '''
        Reads the DP IDR register.
        '''
        rsp = self._usb_xfer_in(bytes(b'\xF2\x22'), 4)
        return unpack('<I', rsp)[0]

    def _read_idcodes(self):
        '''
        Reads "IDCODES".  Not entirely sure what this is.
        '''
        rsp = self._usb_xfer_in(bytes(b'\xF2\x31'), None)
        return unpack('<III', rsp)

    def _current_mode(self):
        rsp = self._usb_xfer_in(bytes(b'\xF5'), 2)
        return rsp[0]

    def _mode_leave(self, mode):
        cmd = MODE_EXIT_CMD.get(mode)
        if cmd:
            self._usb_xfer_null(cmd)

    def _leave_current_mode(self):
        self._mode_leave(self._current_mode())

    def _swd_connect(self):
        # Switch to SWD mode.
        self._leave_current_mode()
        self._cmd_allow_retry(bytes(b'\xF2\x30\xA3'), 2)
        assert self._current_mode() == 0x02

    def _bulk_read_8(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of bytes from the specified address.
        '''
        assert n <= self.max_rw8
        if not n:
            return bytes(b'')
        assert (addr & 0xFFFFFC00) == ((addr + n - 1) & 0xFFFFFC00)
        cmd = pack('<BBIHB', 0xF2, 0x0C, addr, n, ap_num)
        rsp = self._usb_xfer_in(cmd, 2 if n == 1 else n)
        err = self._usb_last_xfer_status()
        if err[0] != 0x80:
            raise Exception('Unexpected error 0x%02X: %s' % (err[0], err))
        return bytes(rsp[:n])

    def _bulk_read_16(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of 16-bit halfwords from the 16-bit aligned
        addr.
        '''
        assert self.features & FEATURE_BULK_READ_16
        assert addr % 2 == 0
        if not n:
            return bytes(b'')
        assert (addr & 0xFFFFFC00) == ((addr + n*2 - 1) & 0xFFFFFC00)
        cmd = pack('<BBIHB', 0xF2, 0x47, addr, n*2, ap_num)
        rsp = self._usb_xfer_in(cmd, n*2)
        err = self._usb_last_xfer_status()
        if err[0] != 0x80:
            raise Exception('Unexpected error 0x%02X: %s' % (err[0], err))
        return bytes(rsp)

    def _bulk_read_32(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of 32-bit words from the 32-bit aligned addr.
        '''
        assert addr % 4 == 0
        if not n:
            return bytes(b'')
        assert (addr & 0xFFFFFC00) == ((addr + n*4 - 1) & 0xFFFFFC00)
        cmd = pack('<BBIHB', 0xF2, 0x07, addr, n*4, ap_num)
        rsp = self._usb_xfer_in(cmd, n*4)
        err = self._usb_last_xfer_status()
        if err[0] != 0x80:
            raise Exception('Unexpected error 0x%02X: %s' % (err[0], err))
        return bytes(rsp)

    def _bulk_write_8(self, data, addr, ap_num=0):
        '''
        Writes a consecutive number of bytes to the specified address.
        '''
        assert len(data) <= self.max_rw8
        if not data:
            return
        assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)
        self._usb_xfer_out(pack('<BBIHB', 0xF2, 0x0D, addr, len(data), ap_num),
                           data)

    def _bulk_write_16(self, data, addr, ap_num=0):
        '''
        Writes a consecutive number of 16-bit halfwords to the 16-bit aligned
        addr.
        '''
        assert addr % 2 == 0
        assert len(data) % 2 == 0
        if not data:
            return
        assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)
        self._usb_xfer_out(pack('<BBIHB', 0xF2, 0x48, addr, len(data), ap_num),
                           data)

    def _bulk_write_32(self, data, addr, ap_num=0):
        '''
        Writes a consecutive number of 32-bit words to the 32-bit aligned addr.
        '''
        assert addr % 4 == 0
        assert len(data) % 4 == 0
        if not data:
            return
        assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)
        self._usb_xfer_out(pack('<BBIHB', 0xF2, 0x08, addr, len(data), ap_num),
                           data)

    def _should_offload_ap(self, ap_num):
        '''
        Decide whether or not we should offload AP accesses to the debug probe.
        If there is no populated AP then we have to offload since we don't have
        a class instance to maintain the AP state; otherwise, if there is an AP
        and we've detected it to be an AHBAP then it's safe to offload to the
        probe.  For other types of AP, the debug probe will clobber the upper
        bits of the CSW register and this can have bad side effects such as
        preventing the CPU from accessing debug hardware (i.e. by clearing
        CSW.DbgSwEnable).
        '''
        ap = self.aps.get(ap_num)
        return ap and isinstance(ap, psdb.access_port.AHBAP)

    def assert_srst(self):
        '''Holds the target in reset.'''
        self._cmd_allow_retry(bytes(b'\xF2\x3C\x00'), 2)

    def deassert_srst(self):
        '''Releases the target from reset.'''
        self._cmd_allow_retry(bytes(b'\xF2\x3C\x01'), 2)

    def set_tck_freq(self, freq):
        raise NotImplementedError

    def read_ap_reg(self, apsel, addr):
        '''Read a 32-bit register from the AP address space.'''
        cmd = pack('<BBHB', 0xF2, 0x45, apsel, addr)
        rsp = self._cmd_allow_retry(cmd, 8)
        return unpack_from('<I', rsp, 4)[0]

    def write_ap_reg(self, apsel, addr, value):
        '''Write a 32-bit register in the AP address space.'''
        cmd = pack('<BBHHI', 0xF2, 0x46, apsel, addr, value)
        self._cmd_allow_retry(cmd, None)

    def read_32(self, addr, ap_num=0):
        '''
        Reads a 32-bit word from the 32-bit aligned addr.  This is more
        efficient than using _bulk_read_32() since the error is returned
        atomically in the same transaction.
        '''
        if not self._should_offload_ap(ap_num):
            return self.aps[ap_num]._read_32(addr)

        assert addr % 4 == 0
        cmd = pack('<BBIB', 0xF2, 0x36, addr, ap_num)
        return unpack_from('<I', self._cmd_allow_retry(cmd, 8), 4)[0]

    def read_16(self, addr, ap_num=0):
        '''
        Reads a 16-bit word using the 16-bit bulk read command.
        For this to make much sense you'll probably want to use a 16-bit
        aligned address.  Not tested across 32-bit word boundaries.
        '''
        if not self._should_offload_ap(ap_num):
            return self.aps[ap_num]._read_16(addr)
        return unpack_from('<H', self._bulk_read_16(addr, 1, ap_num=ap_num))[0]

    def read_8(self, addr, ap_num=0):
        '''
        Reads an 8-bit value using the 8-bit bulk read command.  Unclear
        whether or not this actually performs a single 8-bit access since the
        8-bit bulk read actually returns 2 bytes if you do a single-byte read.
        '''
        if not self._should_offload_ap(ap_num):
            return self.aps[ap_num]._read_8(addr)
        return (unpack_from('<H', self._bulk_read_8(addr, 1, ap_num=ap_num))[0]
                & 0xFF)

    def read_bulk(self, addr, size, ap_num=0):
        '''
        Do a bulk read operation from the specified address.  If the start or
        end addresses are not word-aligned then multiple transactions will take
        place.  If the address range crosses a 1K page boundary, multiple
        transactions will take place to handle the TAR auto-increment issue.
        '''
        if not self._should_offload_ap(ap_num):
            return self.aps[ap_num]._read_bulk(addr, size)
        return super(STLink, self).read_bulk(addr, size, ap_num)

    def write_32(self, v, addr, ap_num=0):
        '''
        Writes a single 32-bit word to the 32-bit aligned addr.  This is more
        efficient than using _bulk_write_32() since it requires fewer USB
        transactions.
        '''
        if not self._should_offload_ap(ap_num):
            return self.aps[ap_num]._write_32(v, addr)

        assert addr % 4 == 0
        cmd = pack('<BBIIB', 0xF2, 0x35, addr, v, ap_num)
        self._cmd_allow_retry(cmd, 2)

    def write_16(self, v, addr, ap_num=0):
        '''
        Writes a 16-bit value using the 16-bit bulk write command.
        '''
        if not self._should_offload_ap(ap_num):
            return self.aps[ap_num]._write_16(v, addr)
        self._bulk_write_16(pack('<H', v), addr, ap_num)

    def write_8(self, v, addr, ap_num=0):
        '''
        Writes an 8-bit value using the 8-bit bulk read command.
        '''
        if not self._should_offload_ap(ap_num):
            return self.aps[ap_num]._write_8(v, addr)
        self._bulk_write_8(chr(v), addr, ap_num)

    def write_bulk(self, data, addr, ap_num=0):
        '''
        Bulk-writes memory by offloading it to the debug probe.  Currently only
        aligned 32-bit accesses are allowed.
        '''
        if not self._should_offload_ap(ap_num):
            return self.aps[ap_num]._write_bulk(data, addr)
        super(STLink, self).write_bulk(data, addr, ap_num)

    def probe(self, verbose=False):
        self._swd_connect()
        self.dpidr = self._read_dpidr()
        return super(STLink, self).probe(verbose=verbose)
