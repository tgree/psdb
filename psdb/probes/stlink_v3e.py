import usb
from . import stlink

from struct import pack, unpack


MAX_FREQS = 10


class STLinkV3E(stlink.STLink):
    '''
    STLink V3E debug probe.  This can be found on the Nucleo 64 board we have
    for the STM32G475 chip.
    '''
    def __init__(self, usb_dev):
        super(STLinkV3E, self).__init__(usb_dev, 'STLinkV3E')
        self._usb_version()
        assert self.ver_stlink == 3

        self.max_rw8        = 512
        self.features      |= stlink.FEATURE_BULK_READ_16
        self.features      |= stlink.FEATURE_BULK_WRITE_16
        self.features      |= stlink.FEATURE_RW_STATUS_12
        self._swd_freqs_khz = sorted(self._get_com_freq(), reverse=True)

    def _usb_last_xfer_status(self):
        '''
        Returns a 12-byte transfer status; the error code is in the first byte.
        '''
        return self._usb_xfer_in(bytes(b'\xF2\x3E'), 12)

    def _usb_version(self):
        rsp = self._usb_xfer_in(bytes(b'\xFB'), 12)
        (self.ver_stlink,
         self.ver_swim,
         self.ver_jtag,
         self.ver_msd,
         self.ver_bridge,
         _, _, _,
         self.ver_vid,
         self.ver_pid) = unpack('<BBBBBBBBHH', rsp)

    def _get_com_freq(self, is_jtag=False):
        '''
        Returns the list of supported frequencies, in kHz.
        '''
        cmd   = pack('<BBB', 0xF2, 0x62, int(is_jtag))
        rsp   = self._cmd_allow_retry(cmd, 12 + 4*MAX_FREQS)
        count = min(rsp[8], MAX_FREQS)
        return unpack('<' + 'I'*count, rsp[12:12 + count*4])

    def _set_com_freq(self, freq_khz, is_jtag=False):
        '''
        Sets the communication frequency to the highest supported frequency
        that doesn't exceed the requested one.  Returns the actual frequency in
        kHz.
        '''
        assert not is_jtag
        for v in self._swd_freqs_khz:
            if freq_khz >= v:
                cmd = pack('<BBBBI', 0xF2, 0x61, int(is_jtag), 0, v)
                self._cmd_allow_retry(cmd, 8)
                return v

        raise Exception('Requested frequency %u kHz too low; minimum is '
                        '%u kHz.' % (freq_khz, self._swd_freqs_khz[-1]))

    def set_tck_freq(self, freq):
        '''
        Sets the communication frequency to the highest supported frequency
        that doesn't exceed the requested one.  Returns the actual frequency in
        Hz.
        '''
        return self._set_com_freq(freq, is_jtag=False) * 1000

    def show_info(self):
        super(STLinkV3E, self).show_info()
        print(' Firmware Ver: V%uJ%uM%uB%uS%u' % (
            self.ver_stlink, self.ver_jtag, self.ver_msd, self.ver_bridge,
            self.ver_swim))


def enumerate():
    devices = usb.core.find(find_all=True, idVendor=0x0483, idProduct=0x374E)
    return [STLinkV3E(d) for d in devices]
