# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import time

from ..device import Device, Reg32
from ..flash import Flash


def block_in_region(addr, size, region_base, region_len):
    return ((region_base <= addr) and
            (addr + size <= region_base + region_len))


def write_in_region(addr, data, region_base, region_len):
    return block_in_region(addr, len(data), region_base, region_len)


class UnlockedContextManager(object):
    def __init__(self, flash):
        self.flash = flash

    def __enter__(self):
        if self.flash._CR.LOCK:
            self.flash._KEYR = 0x45670123
            self.flash._KEYR = 0xCDEF89AB
            assert not self.flash._CR.LOCK

    def __exit__(self, type, value, traceback):
        self.flash._CR.LOCK = 1


class UnlockedOptionsContextManager(object):
    def __init__(self, flash):
        self.flash = flash

    def __enter__(self):
        if self.flash._CR.OPTLOCK:
            assert not self.flash._CR.LOCK
            self.flash._OPTKEYR = 0x08192A3B
            self.flash._OPTKEYR = 0x4C5D6E7F
            assert not self.flash._CR.OPTLOCK

    def __exit__(self, type, value, traceback):
        self.flash._CR.OPTLOCK = 1


class FLASH(Device, Flash):
    REGS = [Reg32('ACR',        0x00,   [('LATENCY',        3),
                                         ('',               5),
                                         ('PRFTEN',         1),
                                         ('ICEN',           1),
                                         ('DCEN',           1),
                                         ('ICRST',          1),
                                         ('DCRST',          1),
                                         ('',               2),
                                         ('PES',            1),
                                         ('EMPTY',          1),
                                         ]),
            Reg32('KEYR',       0x08,   [('KEY',            32)]),
            Reg32('OPTKEYR',    0x0C,   [('OPTKEY',         32)]),
            Reg32('SR',         0x10,   [('EOP',            1),
                                         ('OPERR',          1),
                                         ('',               1),
                                         ('PROGERR',        1),
                                         ('WRPERR',         1),
                                         ('PGAERR',         1),
                                         ('SIZERR',         1),
                                         ('PGSERR',         1),
                                         ('MISSERR',        1),
                                         ('FASTERR',        1),
                                         ('',               3),
                                         ('OPTNV',          1),
                                         ('RDERR',          1),
                                         ('OPTVERR',        1),
                                         ('BSY',            1),
                                         ('',               1),
                                         ('CFGBSY',         1),
                                         ('PESD',           1),
                                         ]),
            Reg32('CR',         0x14,   [('PG',             1),
                                         ('PER',            1),
                                         ('MER',            1),
                                         ('PNB',            8),
                                         ('',               5),
                                         ('STRT',           1),
                                         ('OPTSTRT',        1),
                                         ('FSTPG',          1),
                                         ('',               5),
                                         ('EOPIE',          1),
                                         ('ERRIE',          1),
                                         ('RDERRIE',        1),
                                         ('OBL_LAUNCH',     1),
                                         ('',               2),
                                         ('OPTLOCK',        1),
                                         ('LOCK',           1),
                                         ]),
            Reg32('ECCR',       0x18,   [('ADDR_ECC',       17),
                                         ('',               3),
                                         ('SYSF_ECC',       1),
                                         ('',               3),
                                         ('ECCCIE',         1),
                                         ('',               1),
                                         ('CPUID',          3),
                                         ('',               1),
                                         ('ECCC',           1),
                                         ('ECCD',           1),
                                         ]),
            Reg32('OPTR',       0x20,   [('RDP',            8),
                                         ('ESE',            1),
                                         ('BOR_LEV',        3),
                                         ('nRST_STOP',      1),
                                         ('nRST_STDBY',     1),
                                         ('nRST_SHDW',      1),
                                         ('',               1),
                                         ('IWDG_SW',        1),
                                         ('IWDG_STOP',      1),
                                         ('IWGD_STDBY',     1),
                                         ('WWDG_SW',        1),
                                         ('',               3),
                                         ('nBOOT1',         1),
                                         ('SRAM2_PE',       1),
                                         ('SRAM2_RST',      1),
                                         ('nSWBOOT0',       1),
                                         ('nBOOT0',         1),
                                         ('',               1),
                                         ('AGC_TRIM',       3),
                                         ]),
            Reg32('PCROP1ASR',  0x24,   [('PCROP1A_STRT',   9)]),
            Reg32('PCROP1AER',  0x28,   [('PCROP1A_END',    9),
                                         ('',               22),
                                         ('PCROP_RDP',      1),
                                         ]),
            Reg32('WRP1AR',     0x2C,   [('WRP1A_STRT',     8),
                                         ('',               8),
                                         ('WRP1A_END',      8),
                                         ]),
            Reg32('WRP1BR',     0x30,   [('WRP1B_STRT',     8),
                                         ('',               8),
                                         ('WRP1B_END',      8),
                                         ]),
            Reg32('PCROP1BSR',  0x34,   [('PCROP1B_STRT',   9)]),
            Reg32('PCROP1BER',  0x38,   [('PCROP1B_END',    9)]),
            Reg32('IPCCBR',     0x3C,   [('IPCCDBA',        14)]),
            Reg32('C2ACR',      0x5C,   [('',               8),
                                         ('PRFTEN',         1),
                                         ('ICEN',           1),
                                         ('',               1),
                                         ('ICRST',          1),
                                         ('',               3),
                                         ('PES',            1),
                                         ]),
            Reg32('C2SR',       0x60,   [('EOP',            1),
                                         ('OPERR',          1),
                                         ('',               1),
                                         ('PROGERR',        1),
                                         ('WRPERR',         1),
                                         ('PGAERR',         1),
                                         ('SIZERR',         1),
                                         ('PGSERR',         1),
                                         ('MISSERR',        1),
                                         ('FASTERR',        1),
                                         ('',               4),
                                         ('RDERR',          1),
                                         ('',               1),
                                         ('BSY',            1),
                                         ('',               1),
                                         ('CFGBSY',         1),
                                         ('PESD',           1),
                                         ]),
            Reg32('C2CR',       0x64,   [('PG',             1),
                                         ('PER',            1),
                                         ('MER',            1),
                                         ('PNB',            8),
                                         ('',               5),
                                         ('STRT',           1),
                                         ('',               1),
                                         ('FSTPG',          1),
                                         ('',               5),
                                         ('EOPIE',          1),
                                         ('ERRIE',          1),
                                         ('RDERRIE',        1),
                                         ]),
            Reg32('SFR',        0x80,   [('SFSA',           8),
                                         ('FSD',            1),
                                         ('',               3),
                                         ('DDS',            1),
                                         ]),
            Reg32('SRRVR',      0x84,   [('SBRV',           18),
                                         ('SBRSA',          5),
                                         ('BRSD',           1),
                                         ('',               1),
                                         ('SNBRSA',         5),
                                         ('NBRSD',          1),
                                         ('C2OPT',          1),
                                         ]),
            ]

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq,
                 otp_base, otp_len, **kwargs):
        Device.__init__(self, target, ap, dev_base, name, FLASH.REGS, **kwargs)
        Flash.__init__(self, mem_base, 4096, target.flash_size // 4096)

        self.target         = target
        self.max_write_freq = max_write_freq
        self.otp_base       = otp_base
        self.otp_len        = otp_len

        optr = self._OPTR.read()
        if optr == 0:
            raise Exception('Unexpected OPTR=0, debug clocks may be disabled; '
                            'try using --srst')
        sfr = self._SFR.read()

        if (optr & (1 << 8)) and not (sfr & (1 << 8)):
            self.secure_flash_base = mem_base + ((sfr & 0x000000FF) * 4096)
        else:
            self.secure_flash_base = mem_base + self.target.flash_size
        self.user_flash_size = self.secure_flash_base - mem_base

        srrvr = self._SRRVR.read()
        if not (srrvr & (1 << 23)):
            self.user_sram2a_size = ((srrvr >> 18) & 0x1F)*1024
        else:
            self.user_sram2a_size = self.target.devs['SRAM2a'].size
        if not (srrvr & (1 << 31)):
            self.user_sram2b_size = ((srrvr >> 25) & 0x1F)*1024
        else:
            self.user_sram2b_size = self.target.devs['SRAM2b'].size

        # Clear OPTVERR if set; the MCU startup is buggy and some revisions
        # always set this bit even though there are no options problems.
        if self._SR.OPTVERR:
            self._SR.OPTVERR = 1

    def _flash_unlocked(self):
        return UnlockedContextManager(self)

    def _options_unlocked(self):
        return UnlockedOptionsContextManager(self)

    def _clear_errors(self):
        self._SR = self._SR

    def _check_errors(self):
        v = self._SR.read()
        if v & 0x0000C3F8:
            raise Exception('Flash operation failed, FLASH_SR=0x%08X' % v)

    def _wait_bsy_clear(self):
        while self._SR.BSY:
            pass

    def set_swd_freq_write(self, verbose=True):
        f = self.target.db.set_tck_freq(self.max_write_freq)
        if verbose:
            print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    def set_swd_freq_read(self, verbose=True):
        f = self.target.set_max_tck_freq()
        if verbose:
            print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    def erase_sector(self, n, verbose=True):
        '''
        Erases the nth sector in flash.
        The sector is verified to be erased before returning.
        '''
        assert 0 <= n and n < self.nsectors

        addr = self.mem_base + n * self.sector_size
        if verbose:
            print('Erasing sector [0x%08X - 0x%08X]...' % (
                    addr, addr + self.sector_size - 1))

        with self._flash_unlocked():
            self._clear_errors()
            self._CR = ((n << 3) | (1 << 1))
            self._CR = ((1 << 16) | (n << 3) | (1 << 1))
            self._wait_bsy_clear()
            self._check_errors()
            self._CR = 0

    def erase_all(self, verbose=True):
        '''
        Erases the entire user area of flash.
        '''
        return self.erase(self.mem_base, self.user_flash_size, verbose=verbose)

    def read(self, addr, length):
        '''
        Reads a region from the flash.
        '''
        return self.ap.read_bulk(addr, length)

    def read_all(self):
        '''
        Reads the entire user area of flash.
        '''
        return self.read(self.mem_base, self.user_flash_size)

    def write(self, addr, data, verbose=True):
        '''
        Writes 8-byte lines of data to the flash.  The address must be
        8-byte aligned and the data to write must be a multiple of 8 bytes in
        length.

        The target region to be written must be in the erased state.
        '''
        assert self.target.is_halted()
        if not data:
            return
        assert len(data) % 8 == 0
        assert addr % 8 == 0
        assert (write_in_region(addr, data, self.mem_base, self.flash_size) or
                write_in_region(addr, data, self.otp_base, self.otp_len))

        if verbose:
            print('Flashing region [0x%08X - 0x%08X]...' % (
                    addr, addr + len(data) - 1))

        with self._flash_unlocked():
            self._clear_errors()
            self._CR = (1 << 0)
            self.ap.write_bulk(data, addr)
            self._wait_bsy_clear()
            self._check_errors()
            self._CR = 0

    def read_otp(self, offset, size):
        '''
        Reads a block of one-time-programmable memory.
        '''
        assert offset + size <= self.otp_len
        return self.ap.read_bulk(self.otp_base + offset, size)

    def is_otp_writeable(self, offset, size, verbose=True):
        '''
        Determines if the selected region of one-time-programmable memory is
        still writeable.
        '''
        return self.read_otp(offset, size) == (b'\xFF'*size)

    def write_otp(self, offset, data, verbose=True):
        '''
        Writes 8-byte lines of data to the one-time-programmable area in flash.
        The address must be 8-byte aligned and the data to write must be a
        multiple of 8 bytes in length.

        The target region to be written must be in the erased state (every 8-
        byte double-word must be exactly 0xFFFFFFFFFFFFFFFF - if any of the 64
        bits has already been written, the entire double-word is no longer
        writeable).
        '''
        assert self.is_otp_writeable(offset, len(data))
        self.write(self.otp_base + offset, data)

    def get_ipccdba(self):
        '''
        Returns the address of the IPCC mailbox data buffer.  Note that in the
        flash this value is stored as a double-word offset in SRAM2; here, we
        convert it to a full 32-bit address.
        '''
        offset = self._IPCCBR.IPCCDBA * 8
        return self.target.devs['SRAM2a'].dev_base + offset

    def _flash_optr(self, new_optr, verbose=True):
        '''
        Records the current option values in flash, but doesn't reset the MCU
        so they won't yet take effect or even read back from the flash
        registers.
        '''
        assert self.target.is_halted()
        old_optr = self._OPTR.read()
        if verbose:
            print('Flashing options (Old OPTR=0x%08X, New OPTR=0x%08X)'
                  % (old_optr, new_optr))
        with self._flash_unlocked():
            with self._options_unlocked():
                self._OPTR = new_optr
                self._clear_errors()
                self._CR = (1 << 17)
                self._wait_bsy_clear()
                self._check_errors()

    def _trigger_obl_launch(self, **kwargs):
        '''
        Set OBL_LAUNCH to trigger a reset of the device using the new options.
        This reset triggers a disconnect of the debug probe, so a full
        target.reprobe() sequence is required.  The correct idiom for use of
        _trigger_obl_launch() is:

            target = target.flash._trigger_obl_launch()
        '''
        UnlockedContextManager(self).__enter__()
        UnlockedOptionsContextManager(self).__enter__()

        # Set OBL_LAUNCH to trigger a reset and load of the new settings.  This
        # causes an exception with the XDS110 (and possibly the ST-Link), so
        # catch it and exit cleanly.
        try:
            self._CR = (1 << 27)
        except Exception:
            pass

        return self.target.wait_reset_and_reprobe(**kwargs)

    def get_options(self):
        options = {}
        optr = self._OPTR.read()
        options['agc_trim']   = ((optr >> 29) & 0x07)
        options['nboot0']     = ((optr >> 27) & 0x01)
        options['nswboot0']   = ((optr >> 26) & 0x01)
        options['sram2_rst']  = ((optr >> 25) & 0x01)
        options['sram2_pe']   = ((optr >> 24) & 0x01)
        options['nboot1']     = ((optr >> 23) & 0x01)
        options['wwdg_sw']    = ((optr >> 19) & 0x01)
        options['iwgd_stdby'] = ((optr >> 18) & 0x01)
        options['iwdg_stop']  = ((optr >> 17) & 0x01)
        options['iwdg_sw']    = ((optr >> 16) & 0x01)
        options['nrst_shdw']  = ((optr >> 14) & 0x01)
        options['nrst_stdby'] = ((optr >> 13) & 0x01)
        options['nrst_stop']  = ((optr >> 12) & 0x01)
        options['bor_lev']    = ((optr >>  9) & 0x07)
        options['ese']        = ((optr >>  8) & 0x01)
        options['rdp']        = ((optr >>  0) & 0xFF)
        return options

    def set_options(self, options, verbose=True, connect_under_reset=False):
        assert options.get('agc_trim',   0) <= 0x07
        assert options.get('nboot0',     0) <= 0x01
        assert options.get('nswboot0',   0) <= 0x01
        assert options.get('sram2_rst',  0) <= 0x01
        assert options.get('sram2_pe',   0) <= 0x01
        assert options.get('nboot1',     0) <= 0x01
        assert options.get('wwdg_sw',    0) <= 0x01
        assert options.get('iwgd_stdby', 0) <= 0x01
        assert options.get('iwdg_stop',  0) <= 0x01
        assert options.get('iwdg_sw',    0) <= 0x01
        assert options.get('nrst_shdw',  0) <= 0x01
        assert options.get('nrst_stdby', 0) <= 0x01
        assert options.get('nrst_stop',  0) <= 0x01
        assert options.get('bor_lev',    0) <= 0x07
        assert options.get('ese',        0) <= 0x01
        assert options.get('rdp',        0) <= 0xFF

        cur_options = self.get_options()
        for k, v in options.items():
            assert k in cur_options
            cur_options[k] = v

        optr  = (self._OPTR.read() & 0x10708000)
        optr |= (cur_options['agc_trim']   << 29)
        optr |= (cur_options['nboot0']     << 27)
        optr |= (cur_options['nswboot0']   << 26)
        optr |= (cur_options['sram2_rst']  << 25)
        optr |= (cur_options['sram2_pe']   << 24)
        optr |= (cur_options['nboot1']     << 23)
        optr |= (cur_options['wwdg_sw']    << 19)
        optr |= (cur_options['iwgd_stdby'] << 18)
        optr |= (cur_options['iwdg_stop']  << 17)
        optr |= (cur_options['iwdg_sw']    << 16)
        optr |= (cur_options['nrst_shdw']  << 14)
        optr |= (cur_options['nrst_stdby'] << 13)
        optr |= (cur_options['nrst_stop']  << 12)
        optr |= (cur_options['bor_lev']    <<  9)
        optr |= (cur_options['ese']        <<  8)
        optr |= (cur_options['rdp']        <<  0)
        self._flash_optr(optr, verbose=verbose)

        return self._trigger_obl_launch(verbose=verbose,
                                        connect_under_reset=connect_under_reset)

    def set_boot_sram1(self, **kwargs):
        '''
        Configures the MCU to boot CPU1 from SRAM1 by updating the options
        register and writing it to flash.  The original options register value
        is returned for saving.
        '''
        return self.set_options({'nboot0'   : 0,
                                 'nswboot0' : 0,
                                 'nboot1'   : 0,
                                 }, **kwargs)

    def set_boot_sysmem(self, **kwargs):
        '''
        Configures the MCU to boot from system memory.
        '''
        return self.set_options({'nboot0'   : 1,
                                 'nswboot0' : 0,
                                 'nboot1'   : 1,
                                 }, **kwargs)

    def set_boot_flash(self, **kwargs):
        '''
        Configures the MCU to boot from flash.
        '''
        return self.set_options({'nboot0'   : 1,
                                 'nswboot0' : 1,
                                 'nboot1'   : 1,
                                 }, **kwargs)

    def is_sram_boot_enabled(self):
        options = self.get_options()
        return (options['nboot0']   == 0 and
                options['nswboot0'] == 0 and
                options['nboot1']   == 0)

    def is_flash_boot_enabled(self):
        options = self.get_options()
        return (options['nboot0']   == 1 and
                options['nswboot0'] == 1 and
                options['nboot1']   == 1)

    def get_st_otp_data_from_key(self, key):
        '''
        Searches the OTP memory for the 8-byte data identified by the specific
        key value.  This is an ST convention and probably not compatible with
        anything we do, but it is useful in the Nucleo boards.
        '''
        assert self.otp_len % 8 == 0

        data = self.read_otp(0, self.otp_len)
        while data:
            if data[-1] == key:
                return data[-8:]
            data = data[:-8]

        return None

    def set_wait_states(self, ws):
        '''
        Sets the number of wait states for the flash.  Should be configured as
        follows:

                |             HCLK4 (MHz)               |
             WS |   Vcore Range 1   |   Vcore Range 2   |
            ----+-------------------+-------------------+
             0  |    <= 18 MHz      |    <= 6 MHz       |
             1  |    <= 36 MHz      |    <= 12 MHz      |
             2  |    <= 54 MHz      |    <= 16 MHz      |
             3  |    <= 64 MHz      |       N/A         |
            ----+-------------------+-------------------+
        '''
        self._ACR.LATENCY = ws
        while self._ACR.LATENCY != ws:
            time.sleep(0.01)
