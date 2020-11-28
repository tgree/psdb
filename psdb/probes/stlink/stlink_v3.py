# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import usb

from . import stlink
from . import cdb
from . import errors
import psdb


V3_PIDS = [0x374E,
           0x374F,
           0x3753,
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
    '''
    def __init__(self, usb_dev):
        super().__init__(usb_dev, 'STLinkV3')
        self._usb_version()
        assert self.ver_stlink == 3

        if self.ver_jtag < 6:
            self.max_rw8 = 64
        else:
            self.max_rw8 = 512

        self.features      |= stlink.FEATURE_BULK_READ_16
        self.features      |= stlink.FEATURE_BULK_WRITE_16
        self.features      |= stlink.FEATURE_RW_STATUS_12
        self.features      |= stlink.FEATURE_VOLTAGE
        self.features      |= stlink.FEATURE_AP
        self.features      |= stlink.FEATURE_OPEN_AP
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

    def set_tck_freq(self, freq_hz):
        '''
        Sets the communication frequency to the highest supported frequency
        that doesn't exceed the requested one.  Returns the actual frequency in
        Hz.
        '''
        return self._set_com_freq(freq_hz // 1000, is_jtag=False) * 1000

    def show_info(self):
        super().show_info()
        print(' Firmware Ver: V%uJ%uM%uB%uS%u' % (
            self.ver_stlink, self.ver_jtag, self.ver_msd, self.ver_bridge,
            self.ver_swim))


def is_stlink_v3(usb_dev):
    return usb_dev.idVendor == 0x0483 and usb_dev.idProduct in V3_PIDS


def enumerate():
    devices = usb.core.find(find_all=True, custom_match=is_stlink_v3)
    return [STLinkV3(d) for d in devices]
