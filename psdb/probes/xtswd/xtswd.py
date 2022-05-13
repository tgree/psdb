# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import serial
import struct

from .. import probe
import psdb.devices


BAUD_RATE = 230400


class XTSWD(probe.Probe):
    def __init__(self, intf):
        super().__init__('XTSWD')
        self.intf = intf
        self.serial = serial.serial_for_url(intf, baudrate=BAUD_RATE, timeout=1,
                                            exclusive=True)

        self.fw_name      = None
        self.platform     = None
        self.fw_version   = None
        self.git_sha1     = None
        self.serial_num   = None
        self.serial_date  = None
        self.refclk_hz    = None
        self.max_pll_hz   = None
        self.startup_err  = None
        self.dpidr        = None
        self.buf          = None
        self._reset_and_synchronize()

    def _readline(self):
        l = self.serial.readline()
        #print(l.strip().decode())
        return l

        while b'\r\n' not in self.buf:
            self.buf = self.buf + self.serial.read(1024)

        l, _, self.buf = self.buf.partition(b'\r\n')
        #print(l.strip().decode())
        return l + b'\r\n'

    def _exec_command(self, cmd):
        #print('CMD: %s' % cmd.decode())
        self.serial.write(cmd + b'\r')
        l = self._readline()
        if not l.startswith(b'S: '):
            raise Exception('Unexpected response: "%s"' % l)
        return l

    def __exec_command(self, cmd):
        print('CMD: %s' % cmd.decode())
        return self._exec_command(cmd)

    def _flush_input(self):
        timeout = self.serial.timeout
        self.serial.timeout = 0
        while self.serial.read_all():
            pass
        self.serial.timeout = timeout

    def _reset_and_synchronize(self):
        self._flush_input()
        self.serial.write(b'R\r')
        self._synchronize()

    def _handle_R_line(self, l):
        # Handle the Reset line.
        assert l.startswith(b'R: ')
        words           = l.split()
        self.fw_name    = words[1].decode()
        self.platform   = words[2].decode()
        self.fw_version = words[3].decode()

    def _handle_G_line(self, l):
        # Handle the Git SHA1 line.
        assert l.startswith(b'G: ')
        self.git_sha1 = l.split()[-1].decode()

    def _handle_I_line(self, l):
        # Handle the Identity line.
        assert l.startswith(b'I: ')
        words            = l.split()
        self.serial_num  = words[1].decode()
        self.serial_date = words[2].decode()

    def _handle_H_line(self, l):
        # Handle the HS clock line.
        assert l.startswith(b'H: HS @ ')
        _, _, r = l.partition(b' @ ')
        words   = r.split()
        assert words[1] == b'MHz'
        self.refclk_hz = int(words[0])*1000000

    def _handle_P_line(self, l):
        # Handle the PLL line.
        assert l.startswith(b'P: Max PLL @ ')
        _, _, r = l.partition(b' @ ')
        words   = r.split()
        assert words[1] == b'Hz'
        self.max_pll_hz = int(words[0])

    def _synchronize(self):
        # Nuke everything.
        self.fw_name      = None
        self.platform     = None
        self.fw_version   = None
        self.git_sha1     = None
        self.serial_num   = None
        self.serial_date  = None
        self.refclk_hz    = None
        self.max_pll_hz   = None
        self.startup_err  = 0
        self.buf          = b''

        # Wait for the Reset line.
        while True:
            l = self._readline()
            if l.startswith(b'R: '):
                break
        self._handle_R_line(l)

        # Handle all other lines.
        while True:
            l = self._readline()
            if l in (b'=\r\n', b'#\r\n'):
                break
            if l.startswith(b'G: '):
                self._handle_G_line(l)
            elif l.startswith(b'I: '):
                self._handle_I_line(l)
            elif l.startswith(b'H: '):
                self._handle_H_line(l)
            elif l.startswith(b'P: '):
                self._handle_P_line(l)
            elif l.startswith(b'e: '):
                self._handle_e_line(l)

    def assert_srst(self):
        self._exec_command(b'RST1')

    def deassert_srst(self):
        self._exec_command(b'RST0')

    def set_tck_freq(self, freq):
        return self.refclk_hz / 16

    def open_ap(self, apsel):
        if not (0 <= apsel <= 8):
            raise Exception('AP %u out of range.' % apsel)

    def _bulk_read(self, addr, n, word_size, ap_num=0):
        assert addr % word_size == 0
        l = self._exec_command(b'BR%u:%u:%u:%08X' % (word_size, ap_num, n,
                                                     addr))
        expected_len = 3 + 2*n*word_size + 2
        if len(l) != expected_len:
            raise Exception('Got %u bytes expected %u: %s' % (
                len(l), expected_len, l))
        return bytes.fromhex(l[3:].strip().decode())

    def _bulk_read_8(self, addr, n, ap_num=0):
        return self._bulk_read(addr, n, 1, ap_num=ap_num)

    def _bulk_read_16(self, addr, n, ap_num=0):
        return self._bulk_read(addr, n, 2, ap_num=ap_num)

    def _bulk_read_32(self, addr, n, ap_num=0):
        return self._bulk_read(addr, n, 4, ap_num=ap_num)

    def _bulk_write(self, data, addr, word_size, ap_num=0):
        assert len(data) % word_size == 0
        assert addr % word_size == 0
        self._exec_command(b'BW%u:%u:%08X%s' % (word_size, ap_num, addr,
                                                data.hex().encode('utf-8')))

    def _bulk_write_8(self, data, addr, ap_num=0):
        self._bulk_write(data, addr, 1, ap_num=ap_num)

    def _bulk_write_16(self, data, addr, ap_num=0):
        self._bulk_write(data, addr, 2, ap_num=ap_num)

    def _bulk_write_32(self, data, addr, ap_num=0):
        self._bulk_write(data, addr, 4, ap_num=ap_num)

    def read_dp_reg(self, addr):
        index = addr // 4
        assert 0 <= index <= 3
        l = self._exec_command(b'DPR%u' % index).strip()
        assert l.startswith(b'S: OK 0x')
        return int(l[-8:], 16)

    def write_dp_reg(self, addr, value):
        index = addr // 4
        assert 0 <= index <= 3
        self._exec_command(b'DPW%u:%08X' % (index, value)).strip()

    def read_ap_reg(self, apsel, addr):
        if not (0 <= apsel <= 8):
            raise Exception('AP %u out of range.' % apsel)
        assert 0 <= addr <= 255
        self.write_dp_reg(0x8, (apsel << 24) | (addr & 0xF0))

        index = (addr & 0xF) // 4
        l = self._exec_command(b'APR%u' % index).strip()
        assert l.startswith(b'S: OK 0x')

        return self.read_dp_reg(0xC)

    def write_ap_reg(self, apsel, addr, value):
        if not (0 <= apsel <= 8):
            raise Exception('AP %u out of range.' % apsel)
        assert 0 <= addr <= 255
        self._exec_command(b'DPW2:%08X' % ((apsel << 24) | (addr & 0xF0)))

        index = (addr & 0xF) // 4
        self._exec_command(b'APW%u:%08X' % (index, value))

    def exec_cmd_list(self, cmd_list):
        cmd = b'XCL'
        for c in cmd_list:
            if isinstance(c, psdb.devices.ReadCommand):
                assert c.ap.db == self
                if c.size == 4:
                    opcode = 0x00
                else:
                    raise Exception('Illegal size %u in cmd list.' % c.size)
                opcode |= (c.ap.ap_num & 0xF)
                cmd = cmd + (b'%02X%08X' % (opcode, c.addr))

        l = self._exec_command(cmd).strip()
        data = bytes.fromhex(l[3:].decode())

        read_vals = []
        pos       = 0
        for c in cmd_list:
            if isinstance(c, psdb.devices.ReadCommand):
                if c.size == 4:
                    read_vals.append(struct.unpack_from('<I', data, pos)[0])
                pos += c.size

        return read_vals

    def connect(self):
        l = self._exec_command(b'CON').strip()
        assert l.startswith(b'S: OK DPIDR=0x')
        self.dpidr = int(l[-8:], 16)
