# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32, Reg32W
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
        v = self.flash._read_cr()
        if v & (1<<31):
            self.flash._write_keyr(0x45670123)
            self.flash._write_keyr(0xCDEF89AB)

    def __exit__(self, type, value, traceback):
        v = self.flash._read_cr()
        self.flash._write_cr(v | (1<<31))


class FLASH(Device, Flash):
    '''
    Driver for the FLASH device on the STM32G4 series of MCUs.
    '''
    REGS = [Reg32 ('ACR',           0x000),
            Reg32 ('PDKEYR',        0x004),
            Reg32W('KEYR',          0x008),
            Reg32W('OPTKEYR',       0x00C),
            Reg32 ('SR',            0x010),
            Reg32 ('CR',            0x014),
            Reg32 ('ECCR',          0x018),
            Reg32 ('OPTR',          0x020, [('RDP',         8),
                                            ('BOR_LEV',     3),
                                            ('',            1),
                                            ('nRST_STOP',   1),
                                            ('nRST_STDBY',  1),
                                            ('nRST_SHDW',   1),
                                            ('',            1),
                                            ('IWDG_SW',     1),
                                            ('IWDG_STOP',   1),
                                            ('IWDG_STDBY',  1),
                                            ('WWDG_SW',     1),
                                            ('BFB2',        1),
                                            ('',            1),
                                            ('DBANK',       1),
                                            ('nBOOT1',      1),
                                            ('SRAM_PE',     1),
                                            ('CCMSRAM_RST', 1),
                                            ('nSWBOOT0',    1),
                                            ('nBOOT0',      1),
                                            ('NRST_MODE',   2),
                                            ('IRHEN',       1),
                                            ]),
            Reg32 ('PCROP1SR',      0x024),
            Reg32 ('PCROP1ER',      0x028),
            Reg32 ('WRP1AR',        0x02C),
            Reg32 ('WRP1BR',        0x030),
            Reg32 ('PCROP2SR',      0x044),
            Reg32 ('PCROP2ER',      0x048),
            Reg32 ('WRP2AR',        0x04C),
            Reg32 ('WRP2BR',        0x050),
            Reg32 ('SEC1R',         0x070),
            Reg32 ('SEC2R',         0x074),
            ]

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq,
                 otp_base, otp_len):
        Device.__init__(self, target, ap, dev_base, name, FLASH.REGS)
        self.otp_base = otp_base
        self.otp_len  = otp_len

        optr = self._read_optr()
        if optr == 0:
            raise Exception('Unexpected OPTR=0, debug clocks may be disabled; '
                            'try using --srst')
        sector_size = 2048 if optr & (1<<22) else 4096
        Flash.__init__(self, mem_base, sector_size,
                       target.flash_size // sector_size)
        self.max_write_freq = max_write_freq

    def _flash_unlocked(self):
        return UnlockedContextManager(self)

    def _clear_errors(self):
        self._write_sr(self._read_sr())

    def _check_errors(self):
        v = self._read_sr()
        if v & 0x0000C3F8:
            raise Exception('Flash operation failed, FLASH_SR=0x%08X' % v)

    def _wait_bsy_clear(self):
        while self._read_sr() & (1 << 16):
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
        The sector is verified to be erased before returning.  This checks if
        the flash banks are swapped and erases the appropriate sector if it
        needs to reverse the numbers.
        '''
        assert 0 <= n and n < self.nsectors

        addr = self.mem_base + n * self.sector_size
        if verbose:
            print('Erasing sector [0x%08X - 0x%08X]...' % (
                    addr, addr + self.sector_size - 1))

        # In dual-bank mode, do the right thing.
        if self.sector_size == 2048:
            syscfg  = self.target.devs['SYSCFG']
            fb_mode = bool(syscfg._read_memrmp() & (1 << 8))
            if not fb_mode and n >= 128:
                bker = (1 << 11)
            elif fb_mode and n < 128:
                bker = (1 << 11)
            else:
                bker = 0
            n = (n % 128)

        with self._flash_unlocked():
            self._clear_errors()
            self._write_cr((n << 3) | (1 << 1) | bker)
            self._write_cr((1 << 16) | (n << 3) | (1 << 1) | bker)
            self._wait_bsy_clear()
            self._check_errors()

    def read(self, addr, length):
        '''
        Reads a region from the flash.
        '''
        return self.ap.read_bulk(addr, length)

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
            self._write_cr(1 << 0)
            self.ap.write_bulk(data, addr)
            self._wait_bsy_clear()
            self._check_errors()

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

    def swap_banks_and_reset(self):
        '''
        Swap the flash banks in dual-bank mode.  This also triggers a reset.
        Note: After resetting the target, it will start executing but it also
        terminates the connection to the debugger (at least, in the case of the
        XDS110) - so this is some sort of real hard reset.  You will not be
        able to communicate with the target beyond this call unless you re-
        probe it.
        '''
        UnlockedContextManager(self).__enter__()
        self._write_optkeyr(0x08192A3B)
        self._write_optkeyr(0x4C5D6E7F)
        self._write_optr(self._read_optr() ^ (1 << 20))
        self._write_cr(1 << 17)
        self._wait_bsy_clear()

        # Set OBL_LAUNCH to trigger a reset and load of the new settings.  This
        # causes an exception with the XDS110 (and possibly the ST-Link), so
        # catch it and exit cleanly.
        try:
            self._write_cr(1 << 27)
        except Exception:
            return

        raise Exception('Expected disconnect exception but never got one.')
