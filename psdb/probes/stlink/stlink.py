# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .. import usb_probe
from . import cdb
from . import errors
import psdb

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
TRACE_EP = 0x82

# Maximum size of data that can be returned in a DATA in operation.
DATA_SIZE = 4096

# Commands to exit DFU, DEBUG or SWIM mode.  We need this table so that we can
# get the probe out of its current mode and into SWD mode.
MODE_EXIT_CMD = {cdb.MODE_DFU:   cdb.LeaveDFUMode(),
                 cdb.MODE_DEBUG: cdb.LeaveDebugMode(),
                 cdb.MODE_SWIM:  cdb.LeaveSWIMMode(),
                 }

# Features supported by various versions of the STLINK firmware.
FEATURE_RW_STATUS_12  = (1 << 0)
FEATURE_SWD_SET_FREQ  = (1 << 1)
FEATURE_BULK_READ_16  = (1 << 2)
FEATURE_BULK_WRITE_16 = (1 << 3)
FEATURE_VOLTAGE       = (1 << 4)
FEATURE_AP            = (1 << 5)
FEATURE_OPEN_AP       = (1 << 6)
FEATURE_SCATTERGATHER = (1 << 7)
FEATURE_TRACE         = (1 << 8)


class STLink(usb_probe.Probe):
    '''
    STLink V2.1 debug probe.  This can be found on the Nucleo 144 board we have
    for the STM32H7xx chip.  The USART3 device from the MCU is connected to the
    debug probe as a virtual COM port.
    '''
    def __init__(self, usb_dev):
        super().__init__(usb_dev)
        self.features     = 0
        self.max_sg_ops   = 0
        self.max_swo_freq = 0

    def _check_xfer_status(self):
        '''
        To be implemented by the subclass to check the XFER status of the last
        data phase for CDBs that don't contain an embedded status code.  This
        should retrieve a status code and invoke cdb.check_status() with the
        result.
        '''
        raise NotImplementedError

    def _read_dpidr(self):
        '''
        To be implemented by the subclass.
        '''
        raise NotImplementedError

    def _exec_cdb(self, cmd, timeout=1000):
        '''
        Executes a CDB by writing it to the TX_EP and then driving the various
        phases according to the CDB flags.
        '''
        assert len(cmd.cdb) == 16
        assert self.usb_dev.write(TX_EP, cmd.cdb) == len(cmd.cdb)

        if cmd.CMD_FLAGS & cdb.HAS_DATA_OUT_PHASE:
            size = self.usb_dev.write(TX_EP, cmd.data_out, timeout=timeout)
            assert size == len(cmd.data_out)

        if cmd.CMD_FLAGS & cdb.HAS_DATA_IN_PHASE:
            rsp = self.usb_dev.read(RX_EP, cmd.RSP_LEN, timeout=timeout)
            if cmd.CMD_FLAGS & cdb.HAS_EMBEDDED_STATUS:
                if rsp[0] != errors.DEBUG_OK:
                    raise errors.STLinkCmdException(cmd.cdb, rsp)
            retval = cmd.decode(rsp)
        else:
            retval = None

        if cmd.CMD_FLAGS & cdb.HAS_STATUS_PHASE:
            self._check_xfer_status()

        return retval

    def _cmd_allow_retry(self, cmd, retries=10, delay=0.1):
        '''
        Executes the CDB, retrying it if necessary based on the status code.

        Returns the decoded response if a response is expected.
        '''
        for _ in range(retries):
            try:
                return self._exec_cdb(cmd)
            except errors.STLinkCmdException as e:
                if e.err not in (errors.SWD_AP_WAIT, errors.SWD_DP_WAIT):
                    raise
            time.sleep(delay)
        raise psdb.ProbeException('Max retries exceeded!')

    def _get_voltage(self):
        '''
        Returns the target voltage.
        '''
        assert self.features & FEATURE_VOLTAGE
        vref_adc, target_adc = self._exec_cdb(cdb.ReadVoltage())
        return 2.4 * target_adc / vref_adc

    def _current_mode(self):
        '''
        Returns the current mode that the probe is in (SWIM, JTAG, SWD, etc.).
        '''
        return self._exec_cdb(cdb.GetCurrentMode())

    def _mode_leave(self, mode):
        '''
        Performs an exit command from the specified mode.  Note that the exit
        command is mode-dependent.
        '''
        cmd = MODE_EXIT_CMD.get(mode)
        if cmd:
            self._exec_cdb(cmd)

    def _leave_current_mode(self):
        '''
        Performs the appropriate exit command for the current mode.
        '''
        self._mode_leave(self._current_mode())

    def _swd_connect(self):
        '''
        Enters SWD mode.
        '''
        mode = self._current_mode()
        if mode != cdb.MODE_DEBUG:
            self._mode_leave(mode)
        else:
            self.trace_disable()
        self._cmd_allow_retry(cdb.SWDConnect())
        assert self._current_mode() == cdb.MODE_DEBUG

    def _bulk_read_8(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of bytes from the specified address.
        '''
        data = bytes(b'')
        while n:
            size  = min(n, self.max_rw8)
            data += self._exec_cdb(cdb.BulkRead8(addr, size, ap_num))
            addr += size
            n    -= size
        return data

    def _bulk_read_16(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of 16-bit halfwords from the 16-bit aligned
        addr.
        '''
        assert self.features & FEATURE_BULK_READ_16
        assert n > 0
        return self._exec_cdb(cdb.BulkRead16(addr, n, ap_num))

    def _bulk_read_32(self, addr, n, ap_num=0):
        '''
        Reads a consecutive number of 32-bit words from the 32-bit aligned addr.
        '''
        assert n > 0
        return self._exec_cdb(cdb.BulkRead32(addr, n, ap_num))

    def _bulk_write_8(self, data, addr, ap_num=0):
        '''
        Writes a consecutive number of bytes to the specified address.
        '''
        while data:
            size = min(len(data), self.max_rw8)
            self._exec_cdb(cdb.BulkWrite8(data[:size], addr, ap_num))
            addr += size
            data  = data[size:]

    def _bulk_write_16(self, data, addr, ap_num=0):
        '''
        Writes a consecutive number of 16-bit halfwords to the 16-bit aligned
        addr.
        '''
        assert self.features & FEATURE_BULK_WRITE_16
        assert data
        self._exec_cdb(cdb.BulkWrite16(data, addr, ap_num))

    def _bulk_write_32(self, data, addr, ap_num=0):
        '''
        Writes a consecutive number of 32-bit words to the 32-bit aligned addr.
        '''
        assert data
        self._exec_cdb(cdb.BulkWrite32(data, addr, ap_num))

    def _get_max_sg_ops(self):
        return self._cmd_allow_retry(cdb.ScatterGatherGetMaxOps())

    def _get_trace_num_bytes(self):
        return self._cmd_allow_retry(cdb.GetTraceNumBytes())

    def assert_srst(self):
        '''Holds the target in reset.'''
        self._cmd_allow_retry(cdb.SetSRST(True))

    def deassert_srst(self):
        '''Releases the target from reset.'''
        self._cmd_allow_retry(cdb.SetSRST(False))

    def open_ap(self, apsel):
        '''Prepares the AP for use.'''
        if self.features & FEATURE_OPEN_AP:
            self._cmd_allow_retry(cdb.OpenAP(apsel))

    def read_dp_reg(self, addr):
        '''
        Read a 32-bit register from the DP address space.  The low-order 4 bits
        are the register offset and the next 4 bits are the DPBANKSEL value.
        For instance, to read the TARGETID register use an address of 0x24.
        '''
        return self.read_ap_reg(0xFFFF, addr)

    def write_dp_reg(self, addr, value):
        '''Write a 32-bit register in the DP address space. '''
        return self.write_ap_reg(0xFFFF, addr, value)

    def read_ap_reg(self, apsel, addr):
        '''Read a 32-bit register from the AP address space.'''
        assert self.features & FEATURE_AP
        return self._cmd_allow_retry(cdb.ReadAPReg(apsel, addr))

    def write_ap_reg(self, apsel, addr, value):
        '''Write a 32-bit register in the AP address space.'''
        assert self.features & FEATURE_AP
        self._cmd_allow_retry(cdb.WriteAPReg(apsel, addr, value))

    def read_32(self, addr, ap_num=0):
        '''
        Reads a 32-bit word from the 32-bit aligned addr.  This is more
        efficient than using _bulk_read_32() since the error is returned
        atomically in the same transaction.
        '''
        return self._cmd_allow_retry(cdb.Read32(addr, ap_num))

    def write_32(self, v, addr, ap_num=0):
        '''
        Writes a single 32-bit word to the 32-bit aligned addr.  This is more
        efficient than using _bulk_write_32() since it requires fewer USB
        transactions.
        '''
        self._cmd_allow_retry(cdb.Write32(addr, v, ap_num))

    def scatter_gather(self, ops):
        '''
        Performs a scatter/gather operation using 32-bit accesses encoded in
        the ops list.
        '''
        assert self.features & FEATURE_SCATTERGATHER
        assert len(ops) <= self.max_sg_ops
        self._cmd_allow_retry(cdb.ScatterGatherOut(ops))
        return self._cmd_allow_retry(cdb.ScatterGatherIn(ops))

    def trace_enable(self, swo_freq_hz, trace_size=4096):
        return self._cmd_allow_retry(cdb.TraceEnable(swo_freq_hz, trace_size))

    def trace_disable(self):
        return self._cmd_allow_retry(cdb.TraceDisable())

    def trace_flush(self, swo_freq_hz, trace_size=4096):
        self.trace_enable(swo_freq_hz, trace_size=trace_size)
        data = self.trace_read(timeout=100)
        if data:
            print('Stale trace data: %s' % data)
        self.trace_disable()
        return data

    def trace_read(self, timeout=1000):
        '''
        Reads as many bytes of trace as possible.
        '''
        n = self._get_trace_num_bytes()
        if n <= 0:
            return None
        rsp = self.usb_dev.read(TRACE_EP, n, timeout=timeout)
        assert len(rsp) == n
        return bytes(rsp)

    def connect(self):
        self._swd_connect()
        self.dpidr = self._read_dpidr()
        if self.features & FEATURE_SCATTERGATHER:
            self.max_sg_ops = self._get_max_sg_ops()
