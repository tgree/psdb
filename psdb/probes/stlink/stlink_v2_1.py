# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import usb
from . import stlink
from . import cdb
import psdb


# Unknown commands sniffed via debugger:
# --------------------------------------------------------
#   Req: f2 4b 00 01 00 00 00 00 00 00 00 00 00 00 00 00
#              AP
#   Rsp: 80 00
# --------------------------------------------------------
#   Req: f2 4c 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#              AP
#   Rsp: 80 00
# --------------------------------------------------------

class STLinkV2_1(stlink.STLink):
    '''
    STLink V2.1 debug probe.  This can be found on the Nucleo 144 board we have
    for the STM32H7xx chip.  The USART3 device from the MCU is connected to the
    debug probe as a virtual COM port.
    '''
    def __init__(self, usb_dev):
        super(STLinkV2_1, self).__init__(usb_dev, 'STLinkV2.1')
        self._usb_version()
        assert self.ver_stlink == 2

        self.max_rw8 = 64
        if self.ver_jtag >= 13:
            self.features |= stlink.FEATURE_VOLTAGE
        if self.ver_jtag >= 15:
            self.features |= stlink.FEATURE_RW_STATUS_12
        if self.ver_jtag >= 22:
            self.features |= stlink.FEATURE_SWD_SET_FREQ
        if self.ver_jtag >= 26:
            self.features |= stlink.FEATURE_BULK_READ_16
            self.features |= stlink.FEATURE_BULK_WRITE_16

    def _usb_last_xfer_status(self):
        if self.features & stlink.FEATURE_RW_STATUS_12:
            cls = cdb.LastXFERStatus12
        else:
            cls = cdb.LastXFERStatus2

        rsp = self._usb_xfer_in(cls.make(), cls.RSP_LEN)
        return cls.decode(rsp)

    def _usb_version(self):
        rsp = self._usb_xfer_in(cdb.Version1.make(), 6)
        (self.ver_stlink,
         self.ver_jtag,
         self.ver_swim,
         self.ver_vid,
         self.ver_pid) = cdb.Version1.decode(rsp)

    def _read_dpidr(self):
        rsp = self._cmd_allow_retry(cdb.ReadIDCodes.make(), 12)
        return cdb.ReadIDCodes.decode(rsp)[0]

    def _set_swdclk_divisor(self, divisor):
        assert self.ver_stlink > 1
        assert self.ver_jtag >= 22
        cmd = cdb.SetSWDCLKDivisor.make(divisor)
        self._cmd_allow_retry(cmd, 2)

    def set_tck_freq(self, freq_hz):
        '''
        Sets the TCK to the nearest frequency that doesn't exceed the
        requested one.  Returns the actual frequency in Hz.
        '''
        assert self.features & stlink.FEATURE_SWD_SET_FREQ

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
            if freq_hz >= f:
                self._set_swdclk_divisor(d)
                return f
        raise psdb.ProbeException('Frequency %s too low!' % freq_hz)

    def show_info(self):
        super(STLinkV2_1, self).show_info()
        print(' Firmware Ver: V%uJ%uS%u' % (self.ver_stlink, self.ver_jtag,
                                            self.ver_swim))


def enumerate():
    devices = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0x374B)
    return [STLinkV2_1(d) for d in devices]
