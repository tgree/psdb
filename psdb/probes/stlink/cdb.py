# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from struct import pack, unpack, unpack_from
from builtins import bytes

from . import errors


# Different modes the probe can be in.
MODE_DFU    = 0
MODE_MASS   = 1
MODE_DEBUG  = 2
MODE_SWIM   = 3
MODE_BOOT   = 4

# Command types
HAS_DATA_OUT_PHASE  = (1 << 0)  # USB write op after the CDB.
HAS_DATA_IN_PHASE   = (1 << 1)  # USB read op after the CDB.
HAS_EMBEDDED_STATUS = (1 << 2)  # Data IN phase has status in first byte.
HAS_STATUS_PHASE    = (1 << 3)  # Full XFER_STATUS phase after CDB/DATA phases.

# Opcode types for scatter/gather commands.
CMD_ADDRESS = 1
CMD_WRITE   = 2
CMD_READ    = 3
CMD_APNUM   = 5


def check_xfer_status(status, fault_addr=None):
    if status == errors.DEBUG_OK:
        return
    msg = 'Unexpected error 0x%02X' % status
    if fault_addr is not None:
        msg += ' at 0x%08X' % fault_addr
    raise errors.STLinkXFERException(status, fault_addr, msg)


class STLinkCommandDecodeNotImplementedError(Exception):
    pass


class STLinkCommand:
    '''
    Attempt at documenting the SLINK command protocol.
    '''
    def __init__(self, cmd):
        assert hasattr(self, 'CMD_FLAGS')
        if self.CMD_FLAGS & HAS_DATA_IN_PHASE:
            assert not (self.CMD_FLAGS & HAS_DATA_OUT_PHASE)
            assert hasattr(self, 'RSP_LEN')
        else:
            assert not hasattr(self, 'RSP_LEN')
        if self.CMD_FLAGS & HAS_DATA_OUT_PHASE:
            assert hasattr(self, 'data_out')
        assert len(cmd) <= 16
        self.cmd = cmd
        self.cdb = cmd + bytes(b'\x00'*(16 - len(cmd)))

    def decode(self, rsp):
        assert self.CMD_FLAGS & HAS_DATA_IN_PHASE


class Version1(STLinkCommand):
    '''
    Returns the version of the STLINK debug probe.

    Availability: All.

    TX_EP (CDB):
        +----------------+
        |      0xF1      |
        +----------------+

    RX_EP (6 bytes):
        +----------------+----------------+---------------------------------+
        |       v0       |       v1       |               VID               |
        +----------------+----------------+---------------------------------+
        |               PID               |
        +---------------------------------+

    (v0 << 8) | v1:
         15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        | v_stlink  |     v_jtag      |     v_swim      |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE
    RSP_LEN   = 6

    def __init__(self):
        super().__init__(pack('<B', 0xF1))

    def decode(self, rsp):
        v0, v1, vid, pid = unpack('<BBHH', rsp)
        v = (v0 << 8) | v1
        v_stlink = (v >> 12) & 0x0F
        v_jtag   = (v >>  6) & 0x3F
        v_swim   = (v >>  0) & 0x3F
        return v_stlink, v_jtag, v_swim, vid, pid


class Version2(STLinkCommand):
    '''
    Returns the version of the STLINK/V3 debug probe.

    Availability: V3.

    TX_EP (CDB):
        +----------------+
        |      0xFB      |
        +----------------+

    RX_EP (12 bytes):
        +----------------+----------------+----------------+----------------+
        |    v_stlink    |    v_swim      |     v_jtag     |     v_msd      |
        +----------------+----------------+----------------+----------------+
        |    v_bridge    |       --       |       --       |       --       |
        +----------------+----------------+----------------+----------------+
        |               VID               |               PID               |
        +---------------------------------+---------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE
    RSP_LEN   = 12

    def __init__(self):
        super().__init__(pack('<B', 0xFB))

    def decode(self, rsp):
        (v_stlink, v_swim, v_jtag, v_msd, v_bridge,
         _, _, _, vid, pid) = unpack('<BBBBBBBBHH', rsp)
        return v_stlink, v_swim, v_jtag, v_msd, v_bridge, vid, pid


class ReadVoltage(STLinkCommand):
    '''
    Reads the target voltage and a 2.4V reference voltage, returning both
    values in ADC units.  The target voltage can be computed using:

        target_voltage = 2.4 * target_adc / vref_adc

    Availability: V3 or V2 with J >= 13.

    TX_EP (CDB):
        +----------------+
        |      0xF7      |
        +----------------+

    RX_EP (8 bytes):
        +-------------------------------------------------------------------+
        |                             vref_adc                              |
        +-------------------------------------------------------------------+
        |                            target_adc                             |
        +-------------------------------------------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE
    RSP_LEN   = 8

    def __init__(self):
        super().__init__(pack('<B', 0xF7))

    def decode(self, rsp):
        vref_adc, target_adc = unpack('<LL', rsp)
        return vref_adc, target_adc


class ReadCoreID(STLinkCommand):
    '''
    Returns the DP DPIDR value.
    See "ARM Debug Interface Architecture Specification ADIv5.0 to ADIv5.2"
    section 2.3.5.

    Availability: All.  ReadIDCodes recommended instead for V2+ since it also
                  returns a status code.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x22      |
        +----------------+----------------+

    RX_EP (4 bytes):
        +-------------------------------------------------------------------+
        |                               DPIDR                               |
        +-------------------------------------------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE
    RSP_LEN   = 4

    def __init__(self):
        super().__init__(pack('<BB', 0xF2, 0x22))

    def decode(self, rsp):
        dpidr, = unpack('<I', rsp)
        return dpidr


class ReadIDCodes(STLinkCommand):
    '''
    Returns the DP DPIDR value.
    See "ARM Debug Interface Architecture Specification ADIv5.0 to ADIv5.2"
    section 2.3.5.

    Availability: V2+.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x31      |
        +----------------+----------------+

    RX_EP (12 bytes):
        +----------------+----------------+----------------+----------------+
        |     STATUS     |       --       |      --        |       --       |
        +----------------+----------------+----------------+----------------+
        |                               DPIDR                               |
        +-------------------------------------------------------------------+
        |                                ???                                |
        +-------------------------------------------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 12

    def __init__(self):
        super().__init__(pack('<BB', 0xF2, 0x31))

    def decode(self, rsp):
        _, _, _, _, dpidr, unknown = unpack('<BBBBII', rsp)
        return dpidr, unknown


class GetCurrentMode(STLinkCommand):
    '''
    Returns the STLINK probe's current mode, which can be one of:

        MODE_DFU    = 0
        MODE_MASS   = 1
        MODE_DEBUG  = 2
        MODE_SWIM   = 3
        MODE_BOOT   = 4

    Availability: All.

    TX_EP (CDB):
        +----------------+
        |      0xF5      |
        +----------------+

    RX_EP (2 bytes):
        +----------------+----------------+
        |      MODE      |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE
    RSP_LEN   = 2

    def __init__(self):
        super().__init__(pack('<B', 0xF5))

    def decode(self, rsp):
        mode, _ = unpack('<BB', rsp)
        return mode


class LeaveDFUMode(STLinkCommand):
    '''
    Leaves DFU mode.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF3      |      0x07      |
        +----------------+----------------+

    RX_EP:
        None
    '''
    CMD_FLAGS = 0

    def __init__(self):
        super().__init__(pack('<BB', 0xF3, 0x07))


class LeaveDebugMode(STLinkCommand):
    '''
    Leaves Debug mode.

    Note: This will deassert SRST if it had previously been asserted via a
          SetSRST command - even if SRST was asserted before we entered debug
          mode.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x21      |
        +----------------+----------------+

    RX_EP:
        None
    '''
    CMD_FLAGS = 0

    def __init__(self):
        super().__init__(pack('<BB', 0xF2, 0x21))


class LeaveSWIMMode(STLinkCommand):
    '''
    Leaves SWIM mode.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF4      |      0x01      |
        +----------------+----------------+

    RX_EP:
        None
    '''
    CMD_FLAGS = 0

    def __init__(self):
        super().__init__(pack('<BB', 0xF4, 0x01))


class SWDConnect(STLinkCommand):
    '''
    Connect to the target using SWD mode.  Note that the debug interface clock
    speed should be set before connecting since this command starts clocking
    the target.

    Availability: Everywhere.

    V3J3-V3J5: Somewhere in here the ability to re-issue SWDConnect without
               leaving debug mode was added, allowing to reconnect to a
               target that has been power cycled or to connect to a target
               while maintaining the SRST state if we were already connected
               previously.

               Note: When re-issuing SWDConnect in this way, trace must first
               be disabled otherwise a subsequent read returns a 0 byte for
               every previously-read byte from the trace buffer - i.e. the
               probe's circular buffer pointers don't get reset properly.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+----------------+
        |      0xF2      |      0x30      |      0xA3      |
        +----------------+----------------+----------------+

    RX_EP (2 bytes):
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 2

    def __init__(self):
        super().__init__(pack('<BBB', 0xF2, 0x30, 0xA3))


class SetSWDCLKDivisor(STLinkCommand):
    '''
    Sets the clock divider for the debug interface.  I probed the clock on a
    Nucleo-H743ZI board using an oscilloscope and it seems like the divisor
    value isn't really a divisor of any specific base clock speed, and it also
    seems like the clock speeds on the scope are not really in sync with the
    clock speeds as documented in the OpenOCD source code.  I measured some of
    the OpenOCD values and documented all the values below for reference:

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

    Availability: V2 with J >= 22.  On V3, use SetComFreq instead.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x43      |             divisor             |
        +----------------+----------------+---------------------------------+

    RX_EP (2 bytes):
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 2

    def __init__(self, divisor):
        super().__init__(pack('<BBH', 0xF2, 0x43, divisor))


class GetComFreqs(STLinkCommand):
    '''
    Returns the list of communication frequencies supported by the debug probe.
    Presumably, the debug probe only supports specific frequencies now instead
    of allowing you to select a divider.

    On OpenOCD, the response size is limited to 52 bytes and if N > 10 the list
    is truncated.  If N < 10, OpenOCD pads the list with zeroes on the end.

    The jtag_or_swd field:
        0 - SWD frequencies
        1 - JTAG frequencies

    Availability: V3.

    TX_EP (CDB):
        +----------------+----------------+----------------+
        |      0xF2      |      0x62      |  jtag_or_swd   |
        +----------------+----------------+----------------+

    RX_EP (52 bytes):
        +----------------+----------------+----------------+----------------+
        |     STATUS     |       --       |      --        |       --       |
        +----------------+----------------+----------------+----------------+
        |                                --                                 |
        +----------------+----------------+----------------+----------------+
        |       N        |       --       |      --        |       --       |
        +----------------+----------------+----------------+----------------+
        |                             freq_khz[0]                           |
        +-------------------------------------------------------------------+
        |                             freq_khz[1]                           |
        +-------------------------------------------------------------------+
        |                                ...                                |
        +-------------------------------------------------------------------+
        |                            freq_khz[N-1]                          |
        +-------------------------------------------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    MAX_FREQS = 10
    RSP_LEN   = 12 + 4*MAX_FREQS

    def __init__(self, is_jtag):
        super().__init__(pack('<BBB', 0xF2, 0x62, int(is_jtag)))

    def decode(self, rsp):
        avail = (len(rsp) - 12) / 4
        count = min(avail, rsp[8], GetComFreqs.MAX_FREQS)
        return unpack('<' + 'I'*count, rsp[12:12 + count*4])


class SetComFreq(STLinkCommand):
    '''
    Sets the communication frequency to the specified value.  Returns the
    actual frequency that was set.  The probe only supports the frequencies
    returned by GetComFreqs() and will select the highest frequency that
    doesn't exceed the requested one.

    Returns STATUS 8 if the requested frequency is lower than the lowest
    supported frequency.

    The jtag_or_swd field:
        0 - SWD frequencies
        1 - JTAG frequencies

    Availability: V3.

    TX_EP (CDB):
        +----------------+----------------+----------------+----------------+
        |      0xF2      |      0x61      |  jtag_or_swd   |       0        |
        +----------------+----------------+----------------+----------------+
        |                             freq_khz                              |
        +-------------------------------------------------------------------+

    RX_EP (8 bytes):
        +----------------+----------------+----------------+----------------+
        |     STATUS     |       --       |      --        |       --       |
        +----------------+----------------+----------------+----------------+
        |                           act_freq_khz                            |
        +----------------+----------------+----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 8

    def __init__(self, freq_khz, is_jtag):
        super().__init__(pack('<BBBBI', 0xF2, 0x61, int(is_jtag), 0, freq_khz))

    def decode(self, rsp):
        _, _, _, _, act_freq_khz = unpack('<BBBBI', rsp)
        return act_freq_khz


class SetSTLinkPrescaler(STLinkCommand):
    '''
    Sets the ST-Link's HCLK prescaler to 1 (default), 2 or 4.

    Availability: V3.

    TX_EP (CDB):
        +----------------+----------------+----------------+
        |      0xF2      |      0x63      |   prescaler    |
        +----------------+----------------+----------------+

    RX_EP (8 bytes):
        +----------------+--------------------------------------------------+
        |     STATUS     |                       --                         |
        +----------------+--------------------------------------------------+
        |                                --                                 |
        +-------------------------------------------------------------------+

    Note that the expected status is 0x40 (JTAG configuration changed) instead
    of the normal 0x80 (OK).
    '''


class BulkRead8(STLinkCommand):
    '''
    Reads the specified number of bytes from the specified AP and address.  One
    of the "last transfer" status commands must be used afterwards to get the
    transfer status since it is not encoded in the response.  The read should
    not cross a 1K page boundary.

    Note that if N == 1 the response will be two bytes long and the second byte
    should be ignored.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x0C      |            addr[31:16]         ...
        +----------------+----------------+---------------------------------+
       ...          addr[15:0]            |              N bytes            |
        +----------------+--------------------------------------------------+
        |       AP       |                   CSW >> 8                       |
        +----------------+--------------------------------------------------+

    RX_EP for N > 1 (N bytes):
        +----------------+----------------+----------------+----------------+
        |    DATA[0]     |      ...       |      ...       |   DATA[N-1]    |
        +----------------+----------------+----------------+----------------+

    RX_EP for N == 1 (2 bytes):
        +----------------+----------------+
        |    DATA[0]     |       --       |
        +----------------+----------------+

    Status should be retrieved via a LastXFERStatus command.
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_STATUS_PHASE

    def __init__(self, addr, n, ap_num):
        assert (addr & 0xFFFFFC00) == ((addr + n - 1) & 0xFFFFFC00)
        self.RSP_LEN = max(n, 2)
        self.N       = n
        super().__init__(pack('<BBIHB', 0xF2, 0x0C, addr, n, ap_num))

    def decode(self, rsp):
        assert len(rsp) == self.RSP_LEN
        return bytes(rsp[:self.N])


class BulkRead16(STLinkCommand):
    '''
    Reads the specified number of halfwords from the specified AP and address.
    One of the "last transfer" status commands must be used afterwards to get
    the transfer status since it is not encoded in the response.  The read
    should not cross a 1K page boundary and the address must be 2-byte aligned.

    Note that the API takes a count of n halfwords, but the CDB itself takes a
    count of N = n*2 bytes.

    Availability: V3+ and V2 with J >= 26.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x47      |            addr[31:16]         ...
        +----------------+----------------+---------------------------------+
       ...          addr[15:0]            |              N bytes            |
        +----------------+--------------------------------------------------+
        |       AP       |                   CSW >> 8                       |
        +----------------+--------------------------------------------------+

    RX_EP (N bytes):
        +---------------------------------+---------------------------------+
        |             DATA[0]             |               ...               |
        +---------------------------------+---------------------------------+
        |               ...               |          DATA[N/2 - 1]          |
        +---------------------------------+---------------------------------+

    Status should be retrieved via a LastXFERStatus command.
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_STATUS_PHASE

    def __init__(self, addr, n, ap_num):
        assert addr % 2 == 0
        assert (addr & 0xFFFFFC00) == ((addr + n*2 - 1) & 0xFFFFFC00)
        self.RSP_LEN = n*2
        super().__init__(pack('<BBIHB', 0xF2, 0x47, addr, n*2, ap_num))

    def decode(self, rsp):
        assert len(rsp) == self.RSP_LEN
        return bytes(rsp)


class BulkRead32(STLinkCommand):
    '''
    Reads the specified number of words from the specified AP and address.
    One of the "last transfer" status commands must be used afterwards to get
    the transfer status since it is not encoded in the response.  The read
    should not cross a 1K page boundary and the address must be 4-byte aligned.

    Note that the API takes a count of n words, but the CDB itself takes a
    count of N = n*4 bytes.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x07      |            addr[31:16]         ...
        +----------------+----------------+---------------------------------+
       ...          addr[15:0]            |              N bytes            |
        +----------------+--------------------------------------------------+
        |       AP       |                   CSW >> 8                       |
        +----------------+--------------------------------------------------+

    RX_EP (N bytes):
        +-------------------------------------------------------------------+
        |                              DATA[0]                              |
        +-------------------------------------------------------------------+
        |                              DATA[1]                              |
        +-------------------------------------------------------------------+
        |                                ...                                |
        +-------------------------------------------------------------------+
        |                           DATA[N/4 - 1]                           |
        +-------------------------------------------------------------------+

    Status should be retrieved via a LastXFERStatus command.
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_STATUS_PHASE

    def __init__(self, addr, n, ap_num):
        assert addr % 4 == 0
        assert (addr & 0xFFFFFC00) == ((addr + n*4 - 1) & 0xFFFFFC00)
        self.RSP_LEN = n*4
        super().__init__(pack('<BBIHB', 0xF2, 0x07, addr, n*4, ap_num))

    def decode(self, rsp):
        assert len(rsp) == self.RSP_LEN
        return bytes(rsp)


class BulkWrite8(STLinkCommand):
    '''
    Writes the specified data to the specified AP and address.  One of the "last
    transfer" status commands must be used afterwards to get the transfer status
    since it is not encoded in the response.  The write should not cross a 1K
    page boundary.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x0D      |            addr[31:16]         ...
        +----------------+----------------+---------------------------------+
       ...          addr[15:0]            |              N bytes            |
        +----------------+--------------------------------------------------+
        |       AP       |                   CSW >> 8                       |
        +----------------+--------------------------------------------------+

    TX_EP (DATA, N bytes):
        +----------------+----------------+----------------+----------------+
        |    DATA[0]     |      ...       |      ...       |   DATA[N-1]    |
        +----------------+----------------+----------------+----------------+

    Status should be retrieved via a LastXFERStatus command.
    '''
    CMD_FLAGS = HAS_DATA_OUT_PHASE | HAS_STATUS_PHASE

    def __init__(self, data, addr, ap_num):
        assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)
        self.data_out = data
        super().__init__(pack('<BBIHB', 0xF2, 0x0D, addr, len(data), ap_num))


class BulkWrite16(STLinkCommand):
    '''
    Writes the data to the specified AP and address.  One of the "last transfer"
    status commands must be used afterwards to get the transfer status since it
    is not encoded in the response.  The write should not cross a 1K page
    boundary, should be a multiple of 2 bytes and the address must be 2-byte
    aligned.

    Availability: V3+ and V2 with J >= 26.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x48      |            addr[31:16]         ...
        +----------------+----------------+---------------------------------+
       ...          addr[15:0]            |              N bytes            |
        +----------------+--------------------------------------------------+
        |       AP       |                   CSW >> 8                       |
        +----------------+--------------------------------------------------+

    TX_EP (DATA, N bytes):
        +---------------------------------+---------------------------------+
        |             DATA[0]             |               ...               |
        +---------------------------------+---------------------------------+
        |               ...               |          DATA[N/2 - 1]          |
        +---------------------------------+---------------------------------+

    Status should be retrieved via a LastXFERStatus command.
    '''
    CMD_FLAGS = HAS_DATA_OUT_PHASE | HAS_STATUS_PHASE

    def __init__(self, data, addr, ap_num):
        assert addr % 2 == 0
        assert len(data) % 2 == 0
        assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)
        self.data_out = data
        super().__init__(pack('<BBIHB', 0xF2, 0x48, addr, len(data), ap_num))


class BulkWrite32(STLinkCommand):
    '''
    Writes the data to the specified AP and address.  One of the "last transfer"
    status commands must be used afterwards to get the transfer status since it
    is not encoded in the response.  The write should not cross a 1K page
    boundary, should be a multiple of 4 bytes and the address must be 4-byte
    aligned.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x08      |            addr[31:16]         ...
        +----------------+----------------+---------------------------------+
       ...          addr[15:0]            |              N bytes            |
        +----------------+--------------------------------------------------+
        |       AP       |                   CSW >> 8                       |
        +----------------+--------------------------------------------------+

    TX_EP (DATA, N bytes):
        +-------------------------------------------------------------------+
        |                              DATA[0]                              |
        +-------------------------------------------------------------------+
        |                              DATA[1]                              |
        +-------------------------------------------------------------------+
        |                                ...                                |
        +-------------------------------------------------------------------+
        |                           DATA[N/4 - 1]                           |
        +-------------------------------------------------------------------+

    Status should be retrieved via a LastXFERStatus command.
    '''
    CMD_FLAGS = HAS_DATA_OUT_PHASE | HAS_STATUS_PHASE

    def __init__(self, data, addr, ap_num):
        assert addr % 4 == 0
        assert len(data) % 4 == 0
        assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)
        self.data_out = data
        super().__init__(pack('<BBIHB', 0xF2, 0x08, addr, len(data), ap_num))


class LastXFERStatus2(STLinkCommand):
    '''
    Checks the status of the last DATA transfer since it is not available in
    address is not available in the event of error.

    Availability: V1 and V2.  LastXFERStatus12 is required for V3 and
                  recommended for V2 with J >= 15.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x3B      |
        +----------------+----------------+

    RX_EP (2 bytes):
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE
    RSP_LEN   = 2

    def __init__(self):
        super().__init__(pack('<BB', 0xF2, 0x3B))

    def decode(self, rsp):
        status, _ = unpack('<BB', rsp)
        return status


class LastXFERStatus12(STLinkCommand):
    '''
    Checks the status of the last DATA transfer since it is not available in
    address is not available in the event of error.

    Availability: V3 and V2 with J >= 15.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x3E      |
        +----------------+----------------+

    RX_EP (12 bytes):
        +----------------+----------------+----------------+----------------+
        |     STATUS     |       --       |       --       |       --       |
        +----------------+----------------+----------------+----------------+
        |                           Fault Address                           |
        +-------------------------------------------------------------------+
        |                                --                                 |
        +-------------------------------------------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE
    RSP_LEN   = 12

    def __init__(self):
        super().__init__(pack('<BB', 0xF2, 0x3E))

    def decode(self, rsp):
        status, _, _, _, fault_addr, _ = unpack('<BBBBII', rsp)
        return status, fault_addr


class SetSRST(STLinkCommand):
    '''
    Asserts or deasserts the nSRST signal to the target MCU.  Note that the API
    takes a parameter to *assert* SRST while the level field has inverse
    polarity.

    Set the level field:
        0 - assert SRST and hold the MCU in reset
        1 - deassert SRST and allow the MCU to run
        2 - pulse SRST?

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+----------------+
        |      0xF2      |      0x3C      |      level     |
        +----------------+----------------+----------------+

    RX_EP (2 bytes):
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 2

    def __init__(self, asserted):
        super().__init__(pack('<BBB', 0xF2, 0x3C, int(not asserted)))


class OpenAP(STLinkCommand):
    '''
    Availability: V2.1 J28 and V3.

    TX_EP (CDB):
        +----------------+----------------+----------------+
        |      0xF2      |      0x4B      |       AP       |
        +----------------+----------------+----------------+

    RX_EP (2 bytes):
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 2

    def __init__(self, ap_num):
        super().__init__(pack('<BBB', 0xF2, 0x4B, ap_num))


class CloseAP(STLinkCommand):
    '''
    Availability: V2.1 J28 and V3.

    TX_EP (CDB):
        +----------------+----------------+----------------+
        |      0xF2      |      0x4C      |       AP       |
        +----------------+----------------+----------------+

    RX_EP (2 bytes):
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 2

    def __init__(self, ap_num):
        super().__init__(pack('<BBB', 0xF2, 0x4C, ap_num))


class ReadAPReg(STLinkCommand):
    '''
    Reads a 32-bit register from the AP register space.  This is mostly useful
    so that we can retrieve the BASE register from the AP, allowing us to find
    the base address of this AP's ROM tables.  Prior to accessing AP register
    space, the AP must be opened using an OpenAP() command on firmware versions
    where OpenAP() is available.

    Specifying an AP of 0xFFFF allows reading from the DP registers instead of
    from an attached AP.  There is no OpenAP() equivalent for DP accesses; DP
    reads require no prior setup.

    According to an OpenOCD commit message, the STLINK supports AP accesses to
    AP numbers 0-8. (Commit 5c55fbb065a829beafa233e5c0c0be56d9664934).
    Attempts to access AP numbers outside this range return STATUS 29.

    Availability: V2.1 J24 and V3.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x45      |               AP                |
        +----------------+----------------+---------------------------------+
        |      ADDR      |
        +----------------+

    RX_EP (8 bytes):
        +----------------+----------------+----------------+----------------+
        |     STATUS     |       --       |       --       |       --       |
        +----------------+----------------+----------------+----------------+
        |                           Register Value                          |
        +-------------------------------------------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 8

    def __init__(self, ap_num, addr):
        super().__init__(pack('<BBHB', 0xF2, 0x45, ap_num, addr))

    def decode(self, rsp):
        _, _, _, _, reg32 = unpack('<BBBBI', rsp)
        return reg32


class WriteAPReg(STLinkCommand):
    '''
    Writes a 32-bit register in the AP register space.  This does get invoked
    when we probe the sizes supported by an AHBAP or APBAP.  Prior to accessing
    AP register space, the AP must be opened using an OpenAP() command on
    firmware versions where OpenAP() is available.

    Availability: V2.1 J24 and V3.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x46      |               AP                |
        +----------------+----------------+---------------------------------+
        |              ADDR               |            Val[31:16]          ...
        +---------------------------------+---------------------------------+
       ...            Val[15:0]           |
        +---------------------------------+

    RX_EP (2 bytes):
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 2

    def __init__(self, ap_num, addr, value):
        super().__init__(pack('<BBHHI', 0xF2, 0x46, ap_num, addr, value))


class Read32(STLinkCommand):
    '''
    Reads a 32-bit value from the target AP bus space.  This is more efficent
    than a bulk read since the error status is returned as part of the response
    rather than in a separate transaction.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x36      |            addr[31:16]         ...
        +----------------+----------------+----------------+----------------+
       ...          addr[15:0]            |       AP       |
        +----------------+----------------+----------------+

    RX_EP (8 bytes):
        +----------------+----------------+----------------+----------------+
        |     STATUS     |       --       |       --       |       --       |
        +----------------+----------------+----------------+----------------+
        |                           Register Value                          |
        +-------------------------------------------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 8

    def __init__(self, addr, ap_num):
        assert addr % 4 == 0
        super().__init__(pack('<BBIB', 0xF2, 0x36, addr, ap_num))

    def decode(self, rsp):
        _, _, _, _, u32 = unpack('<BBBBI', rsp)
        return u32


class Write32(STLinkCommand):
    '''
    Writes a 32-bit register in the AP bus space.  This is more efficient
    than a bulk write since the error status is returned as part of the
    response rather than in a separate transaction.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x35      |           Addr[31:16]          ...
        +----------------+----------------+---------------------------------+
       ...           Addr[15:0]           |            Val[31:16]          ...
        +---------------------------------+----------------+----------------+
       ...            Val[15:0]           |       AP       |
        +---------------------------------+----------------+

    RX_EP (2 bytes):
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 2

    def __init__(self, addr, v, ap_num):
        assert addr % 4 == 0
        super().__init__(pack('<BBIIB', 0xF2, 0x35, addr, v, ap_num))


class BulkRead32NoIncr(STLinkCommand):
    '''
    Reads the specified number of words from the specified AP and address,
    without incrementing the address between reads.  This is useful for
    accessing a 32-bit FIFO.  One of the "last transfer" status commands must
    be used afterwards to get the transfer status since it is not encoded in
    the response.

    Note that the API takes a count of n words, but the CDB itself takes a
    count of N = n*4 bytes.

    Availability: V3J2, V2J32.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x54      |            addr[31:16]         ...
        +----------------+----------------+---------------------------------+
       ...          addr[15:0]            |              N bytes            |
        +----------------+--------------------------------------------------+
        |       AP       |                   CSW >> 8                       |
        +----------------+--------------------------------------------------+

    RX_EP (N bytes):
        +-------------------------------------------------------------------+
        |                              DATA[0]                              |
        +-------------------------------------------------------------------+
        |                              DATA[1]                              |
        +-------------------------------------------------------------------+
        |                                ...                                |
        +-------------------------------------------------------------------+
        |                           DATA[N/4 - 1]                           |
        +-------------------------------------------------------------------+

    Status should be retrieved via a LastXFERStatus command.
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_STATUS_PHASE

    def __init__(self, addr, n, ap_num):
        assert addr % 4 == 0
        self.RSP_LEN = n*4
        super().__init__(pack('<BBIHB', 0xF2, 0x54, addr, n*4, ap_num))

    def decode(self, rsp):
        assert len(rsp) == self.RSP_LEN
        return bytes(rsp)


class BulkWrite32NoIncr(STLinkCommand):
    '''
    Writes the data to the specified AP and address, without incrementing the
    address between writes.  This is useful for accessing a 32-bit FIFO.  One
    of the "last transfer" status commands must be used afterwards to get the
    transfer status since it is not encoded in the response.

    Availability: V3, V2J26.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x50      |            addr[31:16]         ...
        +----------------+----------------+---------------------------------+
       ...          addr[15:0]            |              N bytes            |
        +----------------+--------------------------------------------------+
        |       AP       |                   CSW >> 8                       |
        +----------------+--------------------------------------------------+

    TX_EP (DATA, N bytes):
        +-------------------------------------------------------------------+
        |                              DATA[0]                              |
        +-------------------------------------------------------------------+
        |                              DATA[1]                              |
        +-------------------------------------------------------------------+
        |                                ...                                |
        +-------------------------------------------------------------------+
        |                           DATA[N/4 - 1]                           |
        +-------------------------------------------------------------------+

    Status should be retrieved via a LastXFERStatus command.
    '''
    CMD_FLAGS = HAS_DATA_OUT_PHASE | HAS_STATUS_PHASE

    def __init__(self, data, addr, ap_num):
        assert addr % 4 == 0
        assert len(data) % 4 == 0
        self.data_out = data
        super().__init__(pack('<BBIHB', 0xF2, 0x50, addr, len(data), ap_num))


class ScatterGatherOut(STLinkCommand):
    '''
    Performs a scatter-gather Read32/Write32 operation.  This command takes
    a single ops list argument, encoded with pairs as follows:

        (CMD_ADDRESS, 32-bit address for subsequent CMD_WRITE ops)
        (CMD_WRITE,   32-bit value to write to current address)
        (CMD_READ,    32-bit address to read from)
        (CMD_APNUM,   AP number to switch to)

    The ops list should (must?) start with a CMD_APNUM entry.  Note that when
    writing the current address does NOT increment, so a CMD_ADDRESS is
    required any time you want to change the write position.

    The maximum op list length is 64 entries on V2 and 1227 entries on V3.

    Availability: V3J2, V2J26.

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x51      |               N[31:16]         ...
        +----------------+----------------+---------------------------------+
       ...            N[15:0]             |
        +---------------------------------+

    TX_EP (DATA, N*5 + PAD(N,4) bytes):
        +----------------+----------------+----------------+----------------+
        |      CMD1      |      CMD2      |      CMD3      |      CMD4     ...
        +----------------+----------------+----------------+----------------+
       ...     ...              ...              ...              ...      ...
        +----------------+----------------+----------------+----------------+
       ...   CMD(N-1)    |      CMDN      |      Pad to 4-byte alignment    |
        +----------------+----------------+---------------------------------+
        |                             Payload 1                             |
        +-------------------------------------------------------------------+
        |                             Payload 2                             |
        +-------------------------------------------------------------------+
        |                                ...                                |
        +-------------------------------------------------------------------+
        |                             Payload N                             |
        +-------------------------------------------------------------------+

        The command opcodes are defined as follows:
            CMD_ADDRESS = 1
            CMD_WRITE   = 2
            CMD_READ    = 3
            CMD_APNUM   = 5

        The payload entries are defined as follows:
            CMD_ADDRESS:    The 32-bit address for a subsequent CMD_WRITE.
            CMD_WRITE:      The 32-bit value to write.
            CMD_READ:       The 32-bit address from which to read.
            CMD_APNUM:      The AP number, encoded as a 32-bit value.

        The result status is retrieved using ScatterGatherIn.
    '''
    CMD_FLAGS = HAS_DATA_OUT_PHASE

    def __init__(self, ops):
        N             = len(ops)
        cmds          = pack('<%uB' % N, *[op[0] for op in ops])
        payloads      = pack('<%uI' % N, *[op[1] for op in ops])
        self.data_out = cmds + b'\x00'*(-N % 4) + payloads
        super().__init__(pack('<BBI', 0xF2, 0x51, N))


class ScatterGatherIn(STLinkCommand):
    '''
    Retrieves the result of a previous ScatterGatherOut command.  Takes as an
    argument the ops list that was used in the original command so that the
    response can be decoded into a list of tuples:

        (CMD1, Error 1, Payload 1)
        ...
        (CMDN, Error N, Payload N)

    Availability: V3J2, V2J26.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x52      |
        +----------------+----------------+

    RX_EP (N*8 bytes):
        +-------------------------------------------------------------------+
        |                             Payload 1                             |
        +-------------------------------------------------------------------+
        |                             Payload 2                             |
        +-------------------------------------------------------------------+
        |                                ...                                |
        +-------------------------------------------------------------------+
        |                             Payload N                             |
        +-------------------------------------------------------------------+
        |                              Error 1                              |
        +-------------------------------------------------------------------+
        |                              Error 2                              |
        +-------------------------------------------------------------------+
        |                                ...                                |
        +-------------------------------------------------------------------+
        |                              Error N                              |
        +-------------------------------------------------------------------+

        Th payload entries are ignored in all cases except reads and are
        returned from the probe as follows:
            CMD_ADDRESS:    0
            CMD_WRITE:      0
            CMD_READ:       The 32-bit read result.
            CMD_APNUM:      0

        The error entries are the standard error status codes used in other
        commands.
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE

    def __init__(self, ops):
        self.RSP_LEN = len(ops) * 8
        super().__init__(pack('<BB', 0xF2, 0x52))
        self.ops = ops

    def decode(self, rsp):
        N      = len(self.ops)
        result = []
        for i, op in enumerate(self.ops):
            payload = unpack_from('<I', rsp, i * 4)
            error   = unpack_from('<I', rsp, (i + N) * 4)
            result.append((op[0], error, payload))

        return result


class ScatterGatherGetMaxOps(STLinkCommand):
    '''
    Get the number of command opcodes that can be processed in a single scatter-
    gather command.  This command only works if the probe is in DEBUG mode.

    Availability: V3J2, V2J26.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x53      |
        +----------------+----------------+

    RX_EP (2 bytes):
        +---------------------------------+
        |      Max supported SG ops       |
        +---------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE
    RSP_LEN   = 2

    def __init__(self):
        super().__init__(pack('<BB', 0xF2, 0x53))

    def decode(self, rsp):
        return unpack('<H', rsp)[0]


class TraceEnable(STLinkCommand):
    '''
    Enable trace of the specified size and at the specified SWO frequency.  The
    V3SET manual indicates that the debug probe has three different internal
    frequencies that it can run at: high-performance frequency, standard
    frequency and low-consumption frequency.  It is unclear how one of these
    three frequencies is selected (the GetComFreqs command returns a list of 7
    frequencies...), however it does say that the probe starts off in high-
    frequency mode and it is up to the toolchain provider to "propose or not
    the frequency selection at the user level."

    In high-frequency mode, the manual later states that VCP and SWV ports can
    baud rates from the following list:

        [384 MHz / presc for presc in 24 to 31] +
        [192 MHz / presc for presc in 16 to 65535]

    Thus the highest SWV frequeny supported is 16 MHz.

    On a G4 MCU (and perhaps others) the SWO frequency is tied to HCLK (the CPU
    clock).  The TPIU has an asynchronous prescaler used to generate SWO by
    dividing HCLK down to the desired frequency.  The SWV frequency used by the
    probe should match the SWO frequency used by the MCU to a tolerance of 3%.

    According to OpenOCD, the maximum trace size is 4096.  It's unclear what
    the units are.

    Availability: V3, V2J13

    TX_EP (CDB):
        +----------------+----------------+---------------------------------+
        |      0xF2      |      0x40      |           Trace size            |
        +----------------+----------------+---------------------------------+
        |                         SWO frequency (Hz)                        |
        +-------------------------------------------------------------------+

    RX_EP (2 bytes)
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 2

    def __init__(self, swo_freq_hz, trace_size):
        super().__init__(pack('<BBHI', 0xF2, 0x40, trace_size, swo_freq_hz))


class TraceDisable(STLinkCommand):
    '''
    Availability: V3, V2J13

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x41      |
        +----------------+----------------+

    RX_EP (2 bytes)
        +----------------+----------------+
        |     STATUS     |       --       |
        +----------------+----------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE | HAS_EMBEDDED_STATUS
    RSP_LEN   = 2

    def __init__(self):
        super().__init__(pack('<BB', 0xF2, 0x41))


class GetTraceNumBytes(STLinkCommand):
    '''
    Get the number of bytes available in the trace buffer.  This command only
    works if the probe is in DEBUG mode.

    Availability: V3, V2J13.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x42      |
        +----------------+----------------+

    RX_EP (2 bytes):
        +---------------------------------+
        |    Number of bytes in trace     |
        +---------------------------------+
    '''
    CMD_FLAGS = HAS_DATA_IN_PHASE
    RSP_LEN   = 2

    def __init__(self):
        super().__init__(pack('<BB', 0xF2, 0x42))

    def decode(self, rsp):
        return unpack('<H', rsp)[0]
