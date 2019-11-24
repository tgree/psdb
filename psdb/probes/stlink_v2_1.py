# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import usb
from . import stlink

from struct import pack, unpack


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
        if self.ver_jtag >= 15:
            self.features |= stlink.FEATURE_RW_STATUS_12
        if self.ver_jtag >= 22:
            self.features |= stlink.FEATURE_SWD_SET_FREQ
        if self.ver_jtag >= 26:
            self.features |= stlink.FEATURE_BULK_READ_16
            self.features |= stlink.FEATURE_BULK_WRITE_16

    def _usb_last_xfer_status(self):
        '''
        Returns a 2-byte or a 12-byte transfer status; the error code is in the
        first byte.  The 12-byte transfer status is available for versions J15
        and later.  The 2-byte version will eventually be deprecated in a
        future probe firmware update.
        '''
        if self.features & stlink.FEATURE_RW_STATUS_12:
            return self._usb_xfer_in(bytes(b'\xF2\x3E'), 12)
        return self._usb_xfer_in(bytes(b'\xF2\x3B'), 2)

    def _usb_version(self):
        rsp = self._usb_xfer_in(bytes(b'\xF1'), 6)
        v0, v1, vid, pid = unpack('<BBHH', rsp)
        v = (v0 << 8) | v1
        self.ver_stlink = (v >> 12) & 0x0F
        self.ver_jtag   = (v >>  6) & 0x3F
        self.ver_swim   = (v >>  0) & 0x3F
        self.ver_vid    = vid
        self.ver_pid    = pid

    def _set_swdclk_divisor(self, divisor):
        assert self.ver_stlink > 1
        assert self.ver_jtag >= 22
        cmd = pack('<BBH', 0xF2, 0x43, divisor)
        self._cmd_allow_retry(cmd, 2)

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
            if freq >= f:
                self._set_swdclk_divisor(d)
                return f
        raise Exception('Frequency %s too low!' % freq)

    def show_info(self):
        super(STLinkV2_1, self).show_info()
        print(' Firmware Ver: V%uJ%uS%u' % (self.ver_stlink, self.ver_jtag,
                                            self.ver_swim))


def enumerate():
    devices = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0x374B)
    return [STLinkV2_1(d) for d in devices]
