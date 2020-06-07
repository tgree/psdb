# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
from . import stlink
from . import cdb
import psdb


class STLinkV3_Base(stlink.STLink):
    '''
    Base class for STLink/V3 probes.
    '''
    def __init__(self, usb_dev, name):
        super(STLinkV3_Base, self).__init__(usb_dev, name)
        self._usb_version()
        assert self.ver_stlink == 3

        self.max_rw8        = 512
        self.features      |= stlink.FEATURE_BULK_READ_16
        self.features      |= stlink.FEATURE_BULK_WRITE_16
        self.features      |= stlink.FEATURE_RW_STATUS_12
        self.features      |= stlink.FEATURE_VOLTAGE
        self._swd_freqs_khz = sorted(self._get_com_freq(), reverse=True)

    def _usb_last_xfer_status(self):
        rsp = self._usb_xfer_in(cdb.LastXFERStatus12.make(), 12)
        return cdb.LastXFERStatus12.decode(rsp)

    def _usb_version(self):
        rsp = self._usb_xfer_in(cdb.Version2.make(), 12)
        (self.ver_stlink,
         self.ver_swim,
         self.ver_jtag,
         self.ver_msd,
         self.ver_bridge,
         self.ver_vid,
         self.ver_pid) = cdb.Version2.decode(rsp)

    def _read_dpidr(self):
        rsp = self._cmd_allow_retry(cdb.ReadIDCodes.make(), 12)
        return cdb.ReadIDCodes.decode(rsp)[0]

    def _get_com_freq(self, is_jtag=False):
        '''
        Returns the list of supported frequencies, in kHz.
        '''
        cmd   = cdb.GetComFreqs.make(is_jtag)
        rsp   = self._cmd_allow_retry(cmd, cdb.GetComFreqs.RSP_LEN)
        return cdb.GetComFreqs.decode(rsp)

    def _set_com_freq(self, freq_khz, is_jtag=False):
        '''
        Sets the communication frequency to the highest supported frequency
        that doesn't exceed the requested one.  Returns the actual frequency in
        kHz.
        '''
        cmd = cdb.SetComFreq.make(freq_khz, is_jtag)
        try:
            rsp = self._cmd_allow_retry(cmd, 8)
            return cdb.SetComFreq.decode(rsp)
        except stlink.STLinkCmdException as e:
            if e.err != 0x08:
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
        super(STLinkV3_Base, self).show_info()
        print(' Firmware Ver: V%uJ%uM%uB%uS%u' % (
            self.ver_stlink, self.ver_jtag, self.ver_msd, self.ver_bridge,
            self.ver_swim))
