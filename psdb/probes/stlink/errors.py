# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import psdb


# Error status codes
SWIM_OK                     = 0x00
SWIM_BUSY                   = 0x01
NO_DEVICE_CONNECTED         = 0x05
COM_FREQ_TOO_LOW_ERROR      = 0x08
JTAG_GET_IDCODE_ERROR       = 0x09
JTAG_WRITE_ERROR            = 0x0C
JTAG_WRITE_VERIFY_ERROR     = 0x0D
SWD_AP_WAIT                 = 0x10
SWD_AP_FAULT                = 0x11
SWD_AP_ERROR                = 0x12
SWD_AP_PARITY_ERROR         = 0x13
SWD_DP_WAIT                 = 0x14
SWD_DP_FAULT                = 0x15
SWD_DP_ERROR                = 0x16
SWD_DP_PARITY_ERROR         = 0x17
SWD_AP_WDATA_ERROR          = 0x18
SWD_AP_STICKY_ERROR         = 0x19
SWD_AP_STICKY_OVERRUN_ERROR = 0x1A
SWD_BAD_AP_ERROR            = 0x1D
JTAG_CONF_CHANGED           = 0x40
DEBUG_OK                    = 0x80
DEBUG_FAULT                 = 0x81

ERROR_TABLE = {
    0x00 : 'SWIM_OK',
    0x01 : 'SWIM_BUSY',
    0x05 : 'NO_DEVICE_CONNECTED',
    0x08 : 'COM_FREQ_TOO_LOW_ERROR',
    0x09 : 'JTAG_GET_IDCODE_ERROR',
    0x0C : 'JTAG_WRITE_ERROR',
    0x0D : 'JTAG_WRITE_VERIFY_ERROR',
    0x10 : 'SWD_AP_WAIT',
    0x11 : 'SWD_AP_FAULT',
    0x12 : 'SWD_AP_ERROR',
    0x13 : 'SWD_AP_PARITY_ERROR',
    0x14 : 'SWD_DP_WAIT',
    0x15 : 'SWD_DP_FAULT',
    0x16 : 'SWD_DP_ERROR',
    0x17 : 'SWD_DP_PARITY_ERROR',
    0x18 : 'SWD_AP_WDATA_ERROR',
    0x19 : 'SWD_AP_STICKY_ERROR',
    0x1A : 'SWD_AP_STICKY_OVERRUN_ERROR',
    0x1D : 'SWD_BAD_AP_ERROR',
    0x80 : 'DEBUG_OK',
    0x81 : 'DEBUG_FAULT',
}


def status_string(status):
    return ERROR_TABLE.get(status, 'Unknown error')


class STLinkCmdException(psdb.ProbeException):
    def __init__(self, cmd, rsp):
        super().__init__('Unexpected error 0x%02X: %s' % (rsp[0], rsp))
        self.cmd = cmd
        self.rsp = rsp
        self.err = rsp[0]


class STLinkXFERException(psdb.ProbeException):
    def __init__(self, status, fault_addr, msg):
        super().__init__(msg)
        self.status     = status
        self.fault_addr = fault_addr
