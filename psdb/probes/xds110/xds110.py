# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .. import usb_probe
import psdb

import usb.core

import errno
import math
from struct import pack, unpack, unpack_from
from builtins import bytes, range


MIN_FW_VERSION = 0x02030014

ENDPOINT_IN  = 0x83
ENDPOINT_OUT = 0x02

MAX_PACKET       = 1024
MAX_DATA_BLOCK   = 4096
USB_PAYLOAD_SIZE = MAX_DATA_BLOCK + 60


def version_string(v):
    return '%u.%u.%u.%u' % (((v & 0xFF000000) >> 24),
                            ((v & 0x00FF0000) >> 16),
                            ((v & 0x0000FF00) >>  8),
                            ((v & 0x000000FF) >>  0))


class XDS110VersionException(psdb.ProbeException):
    def __init__(self, fw_version, min_fw_version):
        super(XDS110VersionException, self).__init__(
            'Firmware version %s is too old, use Code Composer Studio to '
            'upgrade to at least %s.' % (version_string(fw_version),
                                         version_string(min_fw_version)))
        self.fw_version     = fw_version
        self.min_fw_version = min_fw_version


class XDS110CommandException(psdb.ProbeException):
    def __init__(self, error, allowed_errs, response):
        super(XDS110CommandException, self).__init__('XDS110 error %d' % error)
        self.error        = error
        self.allowed_errs = allowed_errs
        self.response     = response


class XDS110(usb_probe.Probe):
    def __init__(self, usb_dev):
        super(XDS110, self).__init__(usb_dev, 'XDS110')
        self.fw_version, self.hw_version = self.xds_version()
        self.csw_bases = {}
        if self.fw_version < MIN_FW_VERSION:
            raise XDS110VersionException(self.fw_version, MIN_FW_VERSION)

    def read(self, n):
        return self.usb_dev.read(ENDPOINT_IN, n, timeout=40000)

    def write(self, data):
        for retry in range(3):
            try:
                return self.usb_dev.write(ENDPOINT_OUT, data)
            except usb.core.USBError as e:
                if e.errno == errno.EPIPE:
                    self.usb_dev.clear_halt(ENDPOINT_OUT)
        return None

    def get_response(self, allowed_errs):
        buf = self.read(MAX_PACKET)
        assert len(buf) >= 7
        assert buf[0] == ord('*')
        size = buf[1] + (buf[2] << 8)
        assert (4 <= size and size <= USB_PAYLOAD_SIZE)
        assert len(buf) - 3 <= size

        rsp   = buf[3:]
        size -= len(rsp)
        while size:
            buf = self.read(MAX_PACKET)
            assert len(buf) <= size
            rsp  += buf
            size -= len(buf)

        s = rsp.tostring()
        err = unpack_from('i', s)[0]
        if err not in allowed_errs:
            raise XDS110CommandException(err, allowed_errs, s)
        return s[4:], err

    def send_command(self, payload):
        assert (len(payload) <= 4096 + 60)
        cmd = pack('<cH', b'*', len(payload)) + payload
        assert self.write(cmd) == len(cmd)

    def execute(self, cmd, expected_len=None, allowed_errs=[0]):
        self.send_command(cmd)
        rsp, err = self.get_response(allowed_errs)
        if err == 0 and expected_len is not None and expected_len != len(rsp):
            print('Unexpected len response: %s (%u, expected %u)' % (
                    repr(rsp), len(rsp), expected_len))
            assert len(rsp) == expected_len
        return rsp, err

    def xds_version(self):
        '''
        Get firmware version and hardware ID.  Usage:

            fw_version, hw_version = xds.xds_version()
        '''
        rsp, _ = self.execute(pack('<B', 0x03), 6)
        return unpack('IH', rsp)

    def xds_set_tck_delay(self, clks):
        '''
        Set TCK delay (to set TCK frequency) in 66.666666... ns steps.  I
        measured this with an oscilloscope and saw the following values:

            0   = 2730 kHz ( 366 ns)
            1   = 2310 kHz ( 433 ns)
            2   = 2000 kHz ( 500 ns)
            3   = 1760 kHz ( 567 ns)
            10  =  967 kHz (1034 ns)
            100 =  142 kHz (7040 ns)

        For the longer values the measurement is less precise.  This implies
        that the probe is generating:

            P_ns = (1100 + clks*200)/3
            F_hz = 30000000/(11 + clks*2)

        Returns the actual clock period in ns.
        '''
        clks = max(clks, 0)
        clks = min(clks, 144)
        self.execute(pack('<BI', 0x04, clks), 0)
        return (1100 + clks*200)/3.

    def xds_set_srst(self, srst):
        '''
        Assert or deassert nSRST signal

        This signal is active-low.  Calling this with the value 0 will assert
        the signal and the target microcontroller goes into reset.  On the
        MSP432 board, for instance, asserting this signal will cause any lit
        LEDs to be turned off, so all of the GPIO outputs are being reset.  The
        target stays in reset until you deassert the signal by calling this
        with the value 1.

        Removing the RST jumper on the MSP432 dev board prevents this command
        from having any effect on the target; this is connected directly to the
        MSP432 RSTn pin (83).
        '''
        self.execute(pack('<BB', 0x0E, srst), 0)

    def cmapi_connect(self):
        '''
        CMAPI connect.  Usage:

            id_code = xds.cmapi_connect()
        '''
        rsp, err = self.execute(pack('<B', 0x0F), 4, allowed_errs=[0, -1141])
        return unpack('I', rsp)[0], err

    def cmapi_disconnect(self):
        '''CMAPI disconnect'''
        self.execute(pack('<B', 0x10), 0)

    def cmapi_acquire(self):
        '''CMAPI acquire'''
        self.execute(pack('<B', 0x11), 0)

    def cmapi_release(self):
        '''CMAPI release'''
        self.execute(pack('<B', 0x12), 0)

    def cmapi_read_dap_reg(self, typ, apsel, addr):
        '''
        CMAPI DAP register read.  It looks like for an AP read:

            apsel = ADDR[31:24]
            addr  = ADDR[ 7: 0]

        and I guess the SELECT register holds ADDR[31:4].  So there's a lot of
        redundancy here that I don't understand.

        For a DP read, it isn't clear that apsel matters.  Probably only
        addr[3:0] matters.  SELECT.DPBANKSEL looks like it does matter.
        '''
        assert (addr & 3) == 0
        rsp, _ = self.execute(pack('<BBBB', 0x15, typ, apsel, addr), 4)
        return unpack('I', rsp)[0]

    def cmapi_write_dap_reg(self, typ, apsel, addr, value):
        '''CMAPI DAP register write'''
        assert (addr & 3) == 0
        self.execute(pack('<BBBBI', 0x16, typ, apsel, addr, value), 0)

    def swd_connect(self):
        '''Switch from JTAG to SWD connection'''
        self.execute(pack('<B', 0x17), 0)

    def swd_disconnect(self):
        '''Switch from SWD to JTAG connection'''
        self.execute(pack('<B', 0x18), 0)

    def _make_dap_cmd(self, cmd):
        par = (cmd >> 4) ^ (cmd & 0x0F)
        par = (par >> 2) ^ (par & 0x03)
        par = (par >> 1) ^ (par & 0x01)
        return cmd | (par << 5)

    def _make_dp_read_request(self, reg):
        return pack('<B', self._make_dap_cmd(((reg << 1) & 0x18) | 0x05))

    def _make_dp_write_request(self, v, reg):
        return pack('<BI', self._make_dap_cmd(((reg << 1) & 0x18) | 0x01), v)

    def _make_ap_read_request(self, reg):
        return pack('<B', self._make_dap_cmd(((reg << 1) & 0x18) | 0x07))

    def _make_ap_write_request(self, v, reg):
        return pack('<BI', self._make_dap_cmd(((reg << 1) & 0x18) | 0x03), v)

    def ocd_dap_request(self, reqs, result_count):
        '''Handle block of DAP requests'''
        cmd = pack('<B', 0x3A) + reqs + b'\x00'
        rsp, _ = self.execute(cmd, result_count*4)
        return unpack('I'*result_count, rsp)

    def ocd_scan_request(self, reqs, result_size):
        '''Handle block of JTAG scan requests'''
        cmd = pack('<B', 0x3B) + reqs
        rsp, _ = self.execute(cmd, result_size)
        return rsp

    def ocd_pathmove(self, path):
        '''Handle PATHMOVE to navigate JTAG states'''
        cmd = pack('<BI', 0x3C, len(path)) + path
        self.execute(cmd, 0)

    def _get_csw_base(self, ap_num):
        csw_base = self.csw_bases.get(ap_num, self.read_ap_reg(ap_num, 0x00))
        self.csw_bases[ap_num] = csw_base
        return csw_base

    def _bulk_read_8(self, addr, n, ap_num=0):
        '''
        Bulk read n 8-bit values.  Must not cross a page boundary.
        '''
        assert n <= 64
        if not n:
            return bytes(b'')
        assert (addr & 0xFFFFFC00) == ((addr + n - 1) & 0xFFFFFC00)

        csw_base = self._get_csw_base(ap_num)
        reqs  = self._make_dp_write_request((ap_num << 24), 0x08)
        reqs += self._make_ap_write_request((csw_base & ~0x37) | 0x10, 0x00)
        reqs += self._make_ap_write_request(addr, 0x04)
        reqs += self._make_ap_read_request(0x0C)*n
        reqs += self._make_dp_read_request(0x0C)
        results = self.ocd_dap_request(reqs, 1 + n)
        mem = bytes(b'')
        for v in results[1:]:
            mem += b'%c' % ((v >> 8*(addr % 4)) & 0xFF)
            addr += 1
        return mem

    def _bulk_read_32(self, addr, n, ap_num=0):
        '''
        Bulk read n aligned 32-bit values.  Must not cross a page boundary.
        '''
        assert addr % 4 == 0
        assert n < 65536//4
        if not n:
            return bytes(b'')
        assert (addr & 0xFFFFFC00) == ((addr + n*4 - 1) & 0xFFFFFC00)

        csw_base = self._get_csw_base(ap_num)
        reqs  = self._make_dp_write_request((ap_num << 24), 0x08)
        reqs += self._make_ap_write_request((csw_base & ~0x37) | 0x12, 0x00)
        reqs += self._make_ap_write_request(addr, 0x04)
        reqs += self._make_ap_read_request(0x0C)*n
        reqs += self._make_dp_read_request(0x0C)
        results = self.ocd_dap_request(reqs, 1 + n)
        r = bytes(b'')
        for v in results[1:]:
            r += b'%c%c%c%c' % (((v >>  0) & 0xFF),
                                ((v >>  8) & 0xFF),
                                ((v >> 16) & 0xFF),
                                ((v >> 24) & 0xFF))
        return r

    def _bulk_write_8(self, data, addr, ap_num=0):
        assert len(data) <= 64
        if not data:
            return
        assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)

        csw_base = self._get_csw_base(ap_num)
        reqs  = self._make_dp_write_request((ap_num << 24), 0x08)
        reqs += self._make_ap_write_request((csw_base & ~0x37) | 0x10, 0x00)
        reqs += self._make_ap_write_request(addr, 0x04)
        for v in data:
            reqs += self._make_ap_write_request((ord(v) << 8*(addr % 4)), 0x0C)
            addr += 1
        reqs += self._make_dp_write_request((ap_num << 24), 0x08)
        self.ocd_dap_request(reqs, 0)

    def _bulk_write_32(self, data, addr, ap_num=0):
        assert addr % 4 == 0
        assert len(data) % 4 == 0
        if not data:
            return
        assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)

        csw_base = self._get_csw_base(ap_num)
        reqs  = self._make_dp_write_request((ap_num << 24), 0x08)
        reqs += self._make_ap_write_request((csw_base & ~0x37) | 0x12, 0x00)
        reqs += self._make_ap_write_request(addr, 0x04)
        for i in range(len(data)//4):
            v     = unpack_from('<I', data, offset=i*4)[0]
            reqs += self._make_ap_write_request(v, 0x0C)
        reqs += self._make_dp_write_request((ap_num << 24), 0x08)
        self.ocd_dap_request(reqs, 0)

    def assert_srst(self):
        '''Holds the target in reset.'''
        self.xds_set_srst(0)

    def deassert_srst(self):
        '''Releases the target from reset.'''
        self.xds_set_srst(1)

    def set_tck_freq(self, freq):
        '''
        Sets TCK to the nearest frequency that doesn't exceed the requested
        one.  Returns the actual frequency in Hz.
        '''
        p_ns = self.xds_set_tck_delay(math.ceil(15000000./freq - 5.5))
        return 1000000000./p_ns

    def read_dp_reg(self, addr):
        '''Read a 32-bit register from the DP address space. '''
        return self.cmapi_read_dap_reg(1, 0, addr)

    def write_dp_reg(self, addr, value):
        '''Write a 32-bit register in the DP address space. '''
        self.cmapi_write_dap_reg(1, 0, addr, value)

    def read_ap_reg(self, apsel, addr):
        '''Read a 32-bit register from the AP address space.'''
        return self.cmapi_read_dap_reg(0, apsel, addr)

    def write_ap_reg(self, apsel, addr, value):
        '''Write a 32-bit register in the AP address space.'''
        self.cmapi_write_dap_reg(0, apsel, addr, value)

    def read_32(self, addr, ap_num=0):
        return unpack('<I', self._bulk_read_32(addr, 1, ap_num))[0]

    def read_16(self, addr, ap_num=0):
        csw_base = self._get_csw_base(ap_num)
        reqs  = self._make_dp_write_request((ap_num << 24), 0x08)
        reqs += self._make_ap_write_request((csw_base & ~0x37) | 0x01, 0x00)
        reqs += self._make_ap_write_request(addr, 0x04)
        reqs += self._make_ap_read_request(0x0C)
        reqs += self._make_dp_read_request(0x0C)
        results = self.ocd_dap_request(reqs, 2)
        v = results[1]
        return ((v >> 8*(addr % 4)) & 0xFFFF)

    def read_8(self, addr, ap_num=0):
        return ord(self._bulk_read_8(addr, 1, ap_num))

    def write_32(self, v, addr, ap_num=0):
        self._bulk_write_32(pack('<I', v), addr, ap_num)

    def write_16(self, v, addr, ap_num=0):
        csw_base = self._get_csw_base(ap_num)
        reqs  = self._make_dp_write_request((ap_num << 24), 0x08)
        reqs += self._make_ap_write_request((csw_base & ~0x37) | 0x01, 0x00)
        reqs += self._make_ap_write_request(addr, 0x04)
        reqs += self._make_ap_write_request(v << 8*(addr % 4), 0x0C)
        reqs += self._make_dp_write_request((ap_num << 24), 0x08)
        self.ocd_dap_request(reqs, 0)

    def write_8(self, v, addr, ap_num=0):
        self._bulk_write_8(bytes([v]), addr, ap_num)

    def probe(self, **kwargs):
        # Deassert SRST in case someone left it asserted.
        self.deassert_srst()

        # Switch to Serial-Wire debug and connect.  The cmapi_connect() call
        # fails if somebody left DPBANKSEL != 0, so nuke it if we get an error
        # and retry.
        self.swd_connect()
        self.dpidr, err = self.cmapi_connect()
        if err == -1141:
            self.write_dp_reg(0x8, 0x00000000)
            self.dpidr, err = self.cmapi_connect()
            assert err == 0
        self.cmapi_acquire()

        # Probe the target.
        return super(XDS110, self).probe(**kwargs)

    def show_info(self):
        super(XDS110, self).show_info()
        print(' Hardware Ver: 0x%04X' % self.hw_version)
        print(' Firmware Ver: %s' % version_string(self.fw_version))


def enumerate():
    devices = usb.core.find(find_all=True, idVendor=0x0451, idProduct=0xBEF3)
    good_devices = []
    for d in devices:
        try:
            good_devices.append(XDS110(d))
        except XDS110VersionException as e:
            print('%s:%s: %s'
                  % (d.bus, '.'.join('%u' % n for n in d.port_numbers), e))

    return good_devices
