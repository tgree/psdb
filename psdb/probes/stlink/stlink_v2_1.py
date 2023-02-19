# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import usb
import psdb
from . import stlink
from . import cdb
from .. import usb_probe


V2_1_PIDS = [0x374B,
             0x3752,
             ]


class STLinkV2_1(stlink.STLink):
    '''
    STLink V2.1 debug probe.  This can be found on the Nucleo 144 board we have
    for the STM32H7xx chip.  The USART3 device from the MCU is connected to the
    debug probe as a virtual COM port.
    '''
    NAME = 'STLinkV2.1'

    def __init__(self, usb_dev):
        super().__init__(usb_dev)
        self._usb_version()
        assert self.ver_stlink == 2

        self.max_rw8 = 64
        if self.ver_jtag >= 13:
            self.features    |= stlink.FEATURE_VOLTAGE
            self.features    |= stlink.FEATURE_TRACE
            self.max_swo_freq = 2000000
        if self.ver_jtag >= 15:
            self.features |= stlink.FEATURE_RW_STATUS_12
        if self.ver_jtag >= 22:
            self.features |= stlink.FEATURE_SWD_SET_FREQ
        if self.ver_jtag >= 24:
            self.features |= stlink.FEATURE_AP
        if self.ver_jtag >= 26:
            self.features |= stlink.FEATURE_BULK_READ_16
            self.features |= stlink.FEATURE_BULK_WRITE_16
        if self.ver_jtag >= 28:
            self.features |= stlink.FEATURE_OPEN_AP
        if self.ver_jtag >= 32:
            self.features |= stlink.FEATURE_SCATTERGATHER

    def _check_xfer_status(self):
        if self.features & stlink.FEATURE_RW_STATUS_12:
            status, fault_addr = self._exec_cdb(cdb.LastXFERStatus12())
        else:
            status     = self._exec_cdb(cdb.LastXFERStatus2())
            fault_addr = None

        cdb.check_xfer_status(status, fault_addr)

    def _usb_version(self):
        (self.ver_stlink,
         self.ver_jtag,
         self.ver_swim,
         self.ver_vid,
         self.ver_pid) = self._exec_cdb(cdb.Version1())

    def _read_dpidr(self):
        return self._cmd_allow_retry(cdb.ReadIDCodes())[0]

    def _set_swdclk_divisor(self, divisor):
        assert self.ver_stlink > 1
        assert self.ver_jtag >= 22
        self._cmd_allow_retry(cdb.SetSWDCLKDivisor(divisor))

    def set_max_burn_tck_freq(self, flash):
        return self.set_tck_freq(flash.max_nowait_write_freq)

    def _set_tck_freq(self, freq_hz):
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

    @staticmethod
    def find():
        def is_stlink_v2_1(usb_dev):
            return usb_dev.idProduct in V2_1_PIDS
        devs = usb.core.find(find_all=True, idVendor=0x0483,
                             custom_match=is_stlink_v2_1)
        return [usb_probe.Enumeration(STLinkV2_1, d) for d in devs]

    def show_detailed_info(self):
        super().show_info(self.usb_dev)
        print(' Firmware Ver: V%uJ%uS%u' % (self.ver_stlink, self.ver_jtag,
                                            self.ver_swim))
