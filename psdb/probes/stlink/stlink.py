# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .. import usb_probe
from . import cdb
import psdb

from struct import pack, unpack_from
from builtins import bytes, range
import time

# The STLINK works kind of like a SCSI device.  There are three types of
# transaction, all of which begin with a command phase and are then followed by
# an optional data phase:
#
#   xfer_in:   CMD16 out, DATA_in
#   xfer_out:  CMD16 out, DATA_out
#   xfer_null: CMD16 out
#
# DATA_in can be actual bulk data (say, if we are reading RAM or flash), in
# which case it doesn't contain an error code.  Or, it could be a response to
# a query or status for an operation, in which case the first byte often
# contains an error code (but this is command-specific).
#
# CMD16 and DATA_out are always written to the TX_EP.  DATA_in is always read
# from the RX_EP.
RX_EP    = 0x81
TX_EP    = 0x01

# Maximum size of data that can be returned in a DATA in operation.
DATA_SIZE = 4096

# Commands to exit DFU, DEBUG or SWIM mode.  We need this table so that we can
# get the probe out of its current mode and into SWD mode.
MODE_EXIT_CMD = {cdb.MODE_DFU:   cdb.LeaveDFUMode.make(),
                 cdb.MODE_DEBUG: cdb.LeaveDebugMode.make(),
                 cdb.MODE_SWIM:  cdb.LeaveSWIMMode.make(),
                 }

# Features supported by various versions of the STLINK firmware.
FEATURE_RW_STATUS_12  = (1 << 0)
FEATURE_SWD_SET_FREQ  = (1 << 1)
FEATURE_BULK_READ_16  = (1 << 2)
FEATURE_BULK_WRITE_16 = (1 << 3)
FEATURE_VOLTAGE       = (1 << 4)


class STLinkCmdException(psdb.ProbeException):
    def __init__(self, cmd, rsp, msg):
        super(psdb.ProbeException, self).__init__(msg)
        self.cmd = cmd
        self.rsp = rsp
        self.err = rsp[0]


class STLinkXFERException(psdb.ProbeException):
    def __init__(self, status, fault_addr, msg):
        super(psdb.ProbeException, self).__init__(msg)
        self.status     = status
        self.fault_addr = fault_addr


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

    def _usb_xfer_in(self, cmd, rx_size, timeout=1000):
        '''
        Writes a 16-byte command to the TX_EP and then reads a response of the
        given rx_size from the RX_EP.  The rx_size parameter can be specified
        as None to avoid enforcing the RX buffer size.  In that case, a
        variable-length response of up to 4096 bytes can be returned and it is
        up to the caller to validate it.
        '''
        assert len(cmd) == 16
        assert self.usb_dev.write(TX_EP, cmd) == len(cmd)
        if rx_size is None:
            return self.usb_dev.read(RX_EP, DATA_SIZE, timeout=timeout)
        rsp = self.usb_dev.read(RX_EP, rx_size, timeout=timeout)
        assert len(rsp) == rx_size
        return rsp

    def _usb_xfer_out(self, cmd, data, timeout=1000):
        '''
        Writes a 16-byte command parameter is less than 16 bytes to the TX_EP
        and then writes the data buffer to the TX_EP.
        '''
        assert len(cmd) == 16
        assert self.usb_dev.write(TX_EP, cmd) == len(cmd)
        assert self.usb_dev.write(TX_EP, data, timeout=timeout) == len(data)

    def _usb_xfer_null(self, cmd):
        '''
        Writes a 16-byte command to the TX_EP.  No data is transferred.
        '''
        assert len(cmd) == 16
        assert self.usb_dev.write(TX_EP, cmd) == len(cmd)

    def _cmd_allow_retry(self, cmd, rx_size, retries=10, delay=0.1):
        '''
        Performs a xfer_in operation, retrying it if necessary based on the
        first byte of the response which is an error code.
        '''
        for _ in range(retries):
            data = self._usb_xfer_in(cmd, rx_size)
            if data[0] == 0x80:
                return data

            if data[0] not in (0x10, 0x14):
                raise STLinkCmdException(cmd, data,
                                         'Unexpected error 0x%02X: %s'
                                         % (data[0], data))
            time.sleep(delay)
        raise psdb.ProbeException('Max retries exceeded!')

    def _usb_last_xfer_status(self):
        '''
        To be implemented by the subclass.  Different STLINK probes get the
        transfer status in different ways.  This should return a tuple of the
        form:

            (status, fault_addr)

        If the fault_addr is not available, None should be returned.
        '''
        raise NotImplementedError

    def _usb_raise_for_status(self, allowed_status=[0x80]):
        '''
        Raises an exception if the last transfer status code is not in the
        allowed_status list.
        '''
        status, fault_addr = self._usb_last_xfer_status()
        if status not in allowed_status:
            msg = 'Unexpected error 0x%02X' % status
            if fault_addr is not None:
                msg += ' at 0x%08X' % fault_addr
            raise STLinkXFERException(status, fault_addr, msg)

    def _read_dpidr(self):
        '''
        To be implemented by the subclass.
        '''
        raise NotImplementedError

    def _get_voltage(self):
        '''
        Returns the target voltage.
        '''
        assert self.features & FEATURE_VOLTAGE
        rsp = self._usb_xfer_in(cdb.ReadVoltage.make(), 8)
        vref_adc, target_adc = cdb.ReadVoltage.decode(rsp)
        return 2.4 * target_adc / vref_adc

    def _current_mode(self):
        '''
        Returns the current mode that the probe is in (SWIM, JTAG, SWD, etc.).
        '''
        rsp = self._usb_xfer_in(cdb.GetCurrentMode.make(), 2)
        return cdb.GetCurrentMode.decode(rsp)

    def _mode_leave(self, mode):
        '''
        Performs an exit command from the specified mode.  Note that the exit
        command is mode-dependent.
        '''
        cmd = MODE_EXIT_CMD.get(mode)
        if cmd:
            self._usb_xfer_null(cmd)

    def _leave_current_mode(self):
        '''
        Performs the appropriate exit command for the current mode.
        '''
        self._mode_leave(self._current_mode())

    def _swd_connect(self):
        '''
        Enters SWD mode.
        '''
        self._leave_current_mode()
        self._cmd_allow_retry(cdb.SWDConnect.make(), 2)
        assert self._current_mode() == cdb.MODE_DEBUG

    def _bulk_read_8(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of bytes from the specified address.
        '''
        assert n <= self.max_rw8
        if not n:
            return bytes(b'')
        cmd = cdb.BulkRead8.make(addr, n, ap_num)
        rsp = self._usb_xfer_in(cmd, 2 if n == 1 else n)
        self._usb_raise_for_status()
        return cdb.BulkRead8.decode(rsp, n)

    def _bulk_read_16(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of 16-bit halfwords from the 16-bit aligned
        addr.
        '''
        assert self.features & FEATURE_BULK_READ_16
        if not n:
            return bytes(b'')
        cmd = cdb.BulkRead16.make(addr, n, ap_num)
        rsp = self._usb_xfer_in(cmd, n*2)
        self._usb_raise_for_status()
        return cdb.BulkRead16.decode(rsp)

    def _bulk_read_32(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of 32-bit words from the 32-bit aligned addr.
        '''
        if not n:
            return bytes(b'')
        cmd = cdb.BulkRead32.make(addr, n, ap_num)
        rsp = self._usb_xfer_in(cmd, n*4)
        self._usb_raise_for_status()
        return cdb.BulkRead32.decode(rsp)

    def _bulk_write_8(self, data, addr, ap_num=0):
        '''
        Writes a consecutive number of bytes to the specified address.
        '''
        assert len(data) <= self.max_rw8
        if not data:
            return
        self._usb_xfer_out(cdb.BulkWrite8.make(data, addr, ap_num), data)
        self._usb_raise_for_status()

    def _bulk_write_16(self, data, addr, ap_num=0):
        '''
        Writes a consecutive number of 16-bit halfwords to the 16-bit aligned
        addr.
        '''
        if not data:
            return
        self._usb_xfer_out(cdb.BulkWrite16.make(data, addr, ap_num), data)
        self._usb_raise_for_status()

    def _bulk_write_32(self, data, addr, ap_num=0):
        '''
        Writes a consecutive number of 32-bit words to the 32-bit aligned addr.
        '''
        if not data:
            return
        self._usb_xfer_out(cdb.BulkWrite32.make(data, addr, ap_num), data)
        self._usb_raise_for_status()

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
        self._cmd_allow_retry(cdb.SetSRST.make(True), 2)

    def deassert_srst(self):
        '''Releases the target from reset.'''
        self._cmd_allow_retry(cdb.SetSRST.make(False), 2)

    def read_ap_reg(self, apsel, addr):
        '''Read a 32-bit register from the AP address space.'''
        cmd = cdb.ReadAPReg.make(apsel, addr)
        rsp = self._cmd_allow_retry(cmd, 8)
        return cdb.ReadAPReg.decode(rsp)

    def write_ap_reg(self, apsel, addr, value):
        '''Write a 32-bit register in the AP address space.'''
        cmd = cdb.WriteAPReg.make(apsel, addr, value)
        self._cmd_allow_retry(cmd, 2)

    def read_32(self, addr, ap_num=0):
        '''
        Reads a 32-bit word from the 32-bit aligned addr.  This is more
        efficient than using _bulk_read_32() since the error is returned
        atomically in the same transaction.
        '''
        if not self._should_offload_ap(ap_num):
            return self.aps[ap_num]._read_32(addr)

        cmd = cdb.Read32.make(addr, ap_num)
        rsp = self._cmd_allow_retry(cmd, 8)
        return cdb.Read32.decode(rsp)

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
        u16 = self._bulk_read_8(addr, 1, ap_num=ap_num)
        return unpack_from('<H', u16)[0] & 0xFF

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

        cmd = cdb.Write32.make(addr, v, ap_num)
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

    def probe(self, **kwargs):
        self._swd_connect()
        self.dpidr = self._read_dpidr()
        return super(STLink, self).probe(**kwargs)
