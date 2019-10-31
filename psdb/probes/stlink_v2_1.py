# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import usb
from . import usb_probe
from . import probe
import psdb

from struct import pack, unpack, unpack_from
from builtins import bytes, range
import time


RX_EP    = 0x81
TX_EP    = 0x01
TRACE_EP = 0x82

SG_SIZE   = 31
DATA_SIZE = 4096

MODE_EXIT_CMD = {0x00: bytes(b'\xF3\x07'), # DFU
                 0x02: bytes(b'\xF2\x21'), # DEBUG
                 0x03: bytes(b'\xF4\x01'), # SWIM
                 }

# Unknown commands sniffed via debugger:
# --------------------------------------------------------
#   Req: f2 4b 00 01 00 00 00 00 00 00 00 00 00 00 00 00
#              AP
#   Rsp: 80 00
# --------------------------------------------------------
# Typically executed after READMEM_32BIT (0xF2 0x07) and
# WRITEMEM_32BIT (0xF2 0x08)
#   Req: f2 3e 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#   Rsp: 80 00 00 00 00 00 00 00 00 00 00 00
# --------------------------------------------------------
#   Req: f2 4c 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#              AP
#   Rsp: 80 00
# --------------------------------------------------------

class STLinkV2_1(usb_probe.Probe):
    '''
    STLink V2.1 debug probe.  This can be found on the Nucleo 144 board we have
    for the STM32H7xx chip.  The USART3 device from the MCU is connected to the
    debug probe as a virtual COM port.
    '''
    def __init__(self, usb_dev):
        super(STLinkV2_1, self).__init__(usb_dev, 'STLink')
        self._usb_version()
        self.dpidr = None

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
        assert self.usb_dev.write(TX_EP, bytes(b'\xF2\x3B')) == 2
        rsp = self.usb_dev.read(RX_EP, 2, timeout=1000)
        assert len(rsp) == 2
        return rsp

    def _usb_weird_xfer_status(self):
        assert self.usb_dev.write(TX_EP, bytes(b'\xF2\x3E')) == 2
        rsp = self.usb_dev.read(RX_EP, 12, timeout=1000)
        assert len(rsp) == 12
        return rsp

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
        assert self.ver_vid == 0x0483
        assert self.ver_pid == 0x374B

    def _read_dpidr(self, suffix=bytes(b'')):
        rsp = self._usb_xfer_in(bytes(b'\xF2\x22') + suffix, 4)
        return unpack('<I', rsp)[0]

    def _read_idcodes(self, suffix=bytes(b'')):
        rsp = self._usb_xfer_in(bytes(b'\xF2\x31') + suffix, None)
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

    def _set_swdclk_divisor(self, divisor):
        assert self.ver_stlink > 1
        assert self.ver_jtag >= 22
        cmd = pack('<BBH', 0xF2, 0x43, divisor)
        self._cmd_allow_retry(cmd, 2)

    def _bulk_read_8(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of bytes from the specified address.
        '''
        assert n <= 64
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
        assert self.ver_jtag >= 26
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
        assert len(data) <= 64
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
        assert self.ver_jtag >= 26
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
        '''
        Sets the TCK to the nearest frequency that doesn't exceed the
        requested one.  Returns the actual frequency in Hz.
        According to OCD divisors map to frequencies as follows:
                    | OCD  | Scope
            Divisor | kHz  |  kHz
            --------+------+------
                  0 | 4000 | 2360
                  1 | 1800 | 1553
                  2 | 1200 | 1230
                  3 |  950 |  960
                  7 |  480 |  484
                 15 |  240 |  245
                 31 |  125 |  123
                 40 |  100 |
                 79 |   50 |
                158 |   25 |
                265 |   15 |
                798 |    5 |
            --------+------+------

        Basically the clock is crap.  We'll just go with the OCD table.
        '''
        freq_map = [(4000000,   0),
                    (1800000,   1),
                    (1200000,   2),
                    ( 950000,   3),
                    ( 480000,   7),
                    ( 240000,  15),
                    ( 125000,  31),
                    ( 100000,  40),
                    (  50000,  79),
                    (  25000, 158),
                    (  15000, 265),
                    (   5000, 798)]
        for f, d in freq_map:
            if freq >= f:
                self._set_swdclk_divisor(d)
                return f
        raise Exception('Frequency %s too low!' % freq)

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
        return super(STLinkV2_1, self).read_bulk(addr, size, ap_num)

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
        super(STLinkV2_1, self).write_bulk(data, addr, ap_num)

    def probe(self, verbose=False):
        self._swd_connect()
        self.dpidr = self._read_dpidr()
        return super(STLinkV2_1, self).probe(verbose=verbose)

    def show_info(self):
        super(STLinkV2_1, self).show_info()
        print(' Firmware Ver: V%uJ%uM%u' % (self.ver_stlink, self.ver_jtag,
                                            self.ver_swim))


def enumerate():
    devices = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0x374B)
    return [STLinkV2_1(d) for d in devices]
