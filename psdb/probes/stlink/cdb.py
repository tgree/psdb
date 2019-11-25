# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from struct import pack, unpack
from builtins import bytes


# Different modes the probe can be in.
MODE_DFU    = 0
MODE_MASS   = 1
MODE_DEBUG  = 2
MODE_SWIM   = 3
MODE_BOOT   = 4


def make_cdb(cmd):
    '''
    Right-pads the specified command with zeroes to make it a 16-byte CDB.
    '''
    assert len(cmd) <= 16
    return cmd + bytes(b'\x00'*(16 - len(cmd)))


class STLinkCommand(object):
    pass


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
    @staticmethod
    def make():
        return make_cdb(pack('<B', 0xF1))

    @staticmethod
    def decode(rsp):
        assert len(rsp) == 6
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
    @staticmethod
    def make():
        return make_cdb(pack('<B', 0xFB))

    @staticmethod
    def decode(rsp):
        (v_stlink, v_swim, v_jtag, v_msd, v_bridge,
         _, _, _, vid, pid) = unpack('<BBBBBBBBHH', rsp)
        return v_stlink, v_swim, v_jtag, v_msd, v_bridge, vid, pid


class ReadCoreID(STLinkCommand):
    '''
    Returns the DP DPIDR value.
    See "ARM Debug Interface Architecture Specification ADIv5.0 to ADIv5.2"
    section 2.3.5.

    Availability: All.  ReadIDCodes recommended instead for V2+.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x22      |
        +----------------+----------------+

    RX_EP (4 bytes):
        +-------------------------------------------------------------------+
        |                               DPIDR                               |
        +-------------------------------------------------------------------+
    '''
    @staticmethod
    def make():
        return make_cdb(pack('<BB', 0xF2, 0x22))

    @staticmethod
    def decode(rsp):
        assert len(rsp) == 4
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
    @staticmethod
    def make():
        return make_cdb(pack('<BB', 0xF2, 0x31))

    @staticmethod
    def decode(rsp):
        assert len(rsp) == 12
        status, _, _, _, dpidr, unknown = unpack('<BBBBII', rsp)
        return dpidr, unknown


class GetCurrentMode(STLinkCommand):
    '''
    Returns the STLINK probe's current mode.

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
    @staticmethod
    def make():
        return make_cdb(pack('<B', 0xF5))

    @staticmethod
    def decode(rsp):
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
    @staticmethod
    def make():
        return make_cdb(pack('<BB', 0xF3, 0x07))


class LeaveDebugMode(STLinkCommand):
    '''
    Leaves Debug mode.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF2      |      0x21      |
        +----------------+----------------+

    RX_EP:
        None
    '''
    @staticmethod
    def make():
        return make_cdb(pack('<BB', 0xF2, 0x21))


class LeaveSWIMMode(STLinkCommand):
    '''
    Leaves Debug mode.

    Availability: All.

    TX_EP (CDB):
        +----------------+----------------+
        |      0xF4      |      0x01      |
        +----------------+----------------+

    RX_EP:
        None
    '''
    @staticmethod
    def make():
        return make_cdb(pack('<BB', 0xF4, 0x01))


class SWDConnect(STLinkCommand):
    '''
    Connect to the target using SWD mode.  Note that the debug interface clock
    speed should be set before connecting since this command starts clocking
    the target.

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
    @staticmethod
    def make():
        return make_cdb(pack('<BBB', 0xF2, 0x30, 0xA3))


def make_set_swdclk_divisor(divisor):
    return make_cdb(pack('<BBH', 0xF2, 0x43, divisor))


def make_get_com_freq(is_jtag):
    return make_cdb(pack('<BBB', 0xF2, 0x62, int(is_jtag)))


def make_set_com_freq(freq_khz, is_jtag):
    return make_cdb(pack('<BBBBI', 0xF2, 0x61, int(is_jtag), 0, freq_khz))


def make_bulk_read_8(addr, n, ap_num):
    '''
    Reads the specified number of bytes from the specified AP and address.
    '''
    assert (addr & 0xFFFFFC00) == ((addr + n - 1) & 0xFFFFFC00)
    return make_cdb(pack('<BBIHB', 0xF2, 0x0C, addr, n, ap_num))


def make_bulk_read_16(addr, n, ap_num):
    '''
    Reads the specified number of halfwords from the specified AP and address.
    '''
    assert addr % 2 == 0
    assert (addr & 0xFFFFFC00) == ((addr + n*2 - 1) & 0xFFFFFC00)
    return make_cdb(pack('<BBIHB', 0xF2, 0x47, addr, n*2, ap_num))


def make_bulk_read_32(addr, n, ap_num):
    '''
    Reads the specified number of words from the specified AP and address.
    '''
    assert addr % 4 == 0
    assert (addr & 0xFFFFFC00) == ((addr + n*4 - 1) & 0xFFFFFC00)
    return make_cdb(pack('<BBIHB', 0xF2, 0x07, addr, n*4, ap_num))


def make_bulk_write_8(data, addr, ap_num):
    '''
    Writes the specified number of bytes to the specified AP and address.
    '''
    assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)
    return make_cdb(pack('<BBIHB', 0xF2, 0x0D, addr, len(data), ap_num))


def make_bulk_write_16(data, addr, ap_num):
    '''
    Writes the specified number of halfwords to the specified AP and address.
    '''
    assert addr % 2 == 0
    assert len(data) % 2 == 0
    assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)
    return make_cdb(pack('<BBIHB', 0xF2, 0x48, addr, len(data), ap_num))


def make_bulk_write_32(data, addr, ap_num):
    '''
    Writes the specified number of words to the specified AP and address.
    '''
    assert addr % 4 == 0
    assert len(data) % 4 == 0
    assert (addr & 0xFFFFFC00) == ((addr + len(data) - 1) & 0xFFFFFC00)
    return make_cdb(pack('<BBIHB', 0xF2, 0x08, addr, len(data), ap_num))


def make_last_xfer_status_2():
    return make_cdb(pack('<BB', 0xF2, 0x3B))


def make_last_xfer_status_12():
    return make_cdb(pack('<BB', 0xF2, 0x3E))


def make_set_srst(asserted):
    return make_cdb(pack('<BBB', 0xF2, 0x3C, int(not asserted)))


def make_read_ap_reg(apsel, addr):
    return make_cdb(pack('<BBHB', 0xF2, 0x45, apsel, addr))


def decode_read_ap_reg(rsp):
    status, _, _, _, reg32 = unpack('<BBBBI', rsp)
    return reg32


def make_write_ap_reg(apsel, addr, value):
    return make_cdb(pack('<BBHHI', 0xF2, 0x46, apsel, addr, value))


def make_read_32(addr, ap_num):
    assert addr % 4 == 0
    return make_cdb(pack('<BBIB', 0xF2, 0x36, addr, ap_num))


def decode_read_32(rsp):
    status, _, _, _, u32 = unpack('<BBBBI', rsp)
    return u32


def make_write_32(addr, v, ap_num):
    assert addr % 4 == 0
    return make_cdb(pack('<BBIIB', 0xF2, 0x35, addr, v, ap_num))
