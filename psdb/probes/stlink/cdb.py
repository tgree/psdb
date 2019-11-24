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
    assert len(cmd) <= 16
    return cmd + bytes(b'\x00'*(16 - len(cmd)))


def make_version_1():
    return make_cdb(pack('<B', 0xF1))


def make_version_2():
    return make_cdb(pack('<B', 0xFB))


def make_read_coreid():
    return make_cdb(pack('<BB', 0xF2, 0x22))


def decode_read_coreid(rsp):
    assert len(rsp) == 4
    dpidr, = unpack('<I', rsp)
    return dpidr


def make_read_idcodes():
    return make_cdb(pack('<BB', 0xF2, 0x31))


def decode_read_idcodes(rsp):
    assert len(rsp) == 12
    status, _, _, _, dpidr, unknown = unpack('<BBBBII', rsp)
    return dpidr, unknown


def make_get_current_mode():
    return make_cdb(pack('<B', 0xF5))


def decode_get_current_mode(rsp):
    mode, _ = unpack('<BB', rsp)
    return mode


def make_mode_leave_dfu():
    return make_cdb(pack('<BB', 0xF3, 0x07))


def make_mode_leave_debug():
    return make_cdb(pack('<BB', 0xF2, 0x21))


def make_mode_leave_swim():
    return make_cdb(pack('<BB', 0xF4, 0x01))


def make_swd_connect():
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
