# Copyright (c) 2020-2021 by Phase Advanced Sensor Systems, Inc.
import usb

import psdb
from psdb.targets.stm32u5 import STM32U5
from . import stlink
from . import cdb
from . import errors
from .. import usb_probe


V3_PIDS = [0x374E,
           0x374F,
           0x3753,
           0x3754,
           ]


class STLinkV3(stlink.STLink):
    '''
    Base class for STLink/V3 probes.  This includes the following device IDs as
    per TN1235 section 5:

        0x374E - STLINK-V3 without bridge functions (V3E)
        0x374F - STLINK-V3 with bridge functions (V3SET)

    This device ID was also observed after converting a V3SET from MSD+VCP to
    2xVCP mode:

        0x3753 - STLINK-V3 in dual-VCP mode (V3SET)

    This device ID was observed after converting two different types of Nucleo
    board from MSD+VCP to just VCP mode:

        0x3754 - STLINK-V3 in single-VCP mode (Nucleo)

    The STLINK-V3 supports a fixed set of frequencies:

        --------
        24.0 MHz
         8.0 MHz
         3.3 MHz
         1.0 MHz
        --------
         200 KHz
          50 KHz
           5 KHz
        --------

    The STLINK-V3 may support up to 24 MHz for reads, however on the H7 if you
    try to flash at 24 MHz it errors out.  I think the ST firmware doesn't deal
    with WAIT acknowledgements properly.
    '''
    NAME = 'STLinkV3'

    def __init__(self, usb_dev):
        super().__init__(usb_dev)
        self._usb_version()
        assert self.ver_stlink == 3

        if self.ver_jtag >= 2:
            self.features |= stlink.FEATURE_SCATTERGATHER
        if self.ver_jtag >= 6:
            self.max_rw8 = 512
        else:
            self.max_rw8 = 64

        # Before J10, if you went too fast while writing to flash you would get
        # WAIT acknowledgements on the SWD bus and the STLINK would blow up.
        # After J10, it seems to handle the WAIT states properly and you can
        # write an H7 at 24 MHz without it dieing.
        if self.ver_jtag >= 10:
            self.features |= stlink.FEATURE_SWD_WAIT_OK

        self.features    |= stlink.FEATURE_BULK_READ_16
        self.features    |= stlink.FEATURE_BULK_WRITE_16
        self.features    |= stlink.FEATURE_RW_STATUS_12
        self.features    |= stlink.FEATURE_VOLTAGE
        self.features    |= stlink.FEATURE_AP
        self.features    |= stlink.FEATURE_OPEN_AP
        self.features    |= stlink.FEATURE_TRACE
        self.max_swo_freq = 24000000
        self._swd_freqs_khz = sorted(self._get_com_freq(), reverse=True)

    def _check_xfer_status(self):
        status, fault_addr = self._exec_cdb(cdb.LastXFERStatus12())
        cdb.check_xfer_status(status, fault_addr)

    def _usb_version(self):
        (self.ver_stlink,
         self.ver_swim,
         self.ver_jtag,
         self.ver_msd,
         self.ver_bridge,
         self.ver_vid,
         self.ver_pid) = self._exec_cdb(cdb.Version2())

    def _read_dpidr(self):
        return self._cmd_allow_retry(cdb.ReadIDCodes())[0]

    def _get_com_freq(self, is_jtag=False):
        '''
        Returns the list of supported frequencies, in kHz.
        '''
        return self._cmd_allow_retry(cdb.GetComFreqs(is_jtag))

    def _set_com_freq(self, freq_khz, is_jtag=False):
        '''
        Sets the communication frequency to the highest supported frequency
        that doesn't exceed the requested one.  Returns the actual frequency in
        kHz.
        '''
        cmd = cdb.SetComFreq(freq_khz, is_jtag)
        try:
            return self._cmd_allow_retry(cmd)
        except errors.STLinkCmdException as e:
            if e.err != errors.COM_FREQ_TOO_LOW_ERROR:
                raise
        if is_jtag:
            raise psdb.ProbeException('Requested JTAG frequency %u kHz too low.'
                                      % freq_khz)
        raise psdb.ProbeException('Requested SWD frequency %u kHz too low; '
                                  'minimum is %u kHz.'
                                  % (freq_khz, self._swd_freqs_khz[-1]))

    def set_max_burn_tck_freq(self, flash):
        # We really have to hack it here.  Before J10, the U5 errors out if you
        # try to write faster than 3.3 MHz.  With J10, then U5 errors out if
        # you try to write faster than 8 MHz.  On all the other platforms I've
        # tested, J10 allows you to go at the max probe speed of 24 MHz, so not
        # sure why it fails on U5.
        if not self.features & stlink.FEATURE_SWD_WAIT_OK:
            return self.set_tck_freq(flash.max_nowait_write_freq)
        if isinstance(self.target, STM32U5):
            return self.set_tck_freq(8000000)
        return self.set_max_target_tck_freq()

    def _set_tck_freq(self, freq_hz):
        '''
        Sets the communication frequency to the highest supported frequency
        that doesn't exceed the requested one.  Returns the actual frequency in
        Hz.
        '''
        return self._set_com_freq(freq_hz // 1000, is_jtag=False) * 1000

    @staticmethod
    def find():
        def is_stlink_v3(usb_dev):
            return usb_dev.idProduct in V3_PIDS
        devs = usb.core.find(find_all=True, idVendor=0x0483,
                             custom_match=is_stlink_v3)
        return [usb_probe.Enumeration(STLinkV3, d) for d in devs]

    def show_detailed_info(self):
        super().show_info(self.usb_dev)
        print(' Firmware Ver: V%uJ%uM%uB%uS%u' % (
            self.ver_stlink, self.ver_jtag, self.ver_msd, self.ver_bridge,
            self.ver_swim))
