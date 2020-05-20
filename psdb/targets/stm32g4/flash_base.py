# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device
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

    def __exit__(self, type, value, traceback):
        self.flash._CR.LOCK = 1


class FLASH_Base(Device, Flash):
    '''
    Common base class for STM32G4 flash devices.
    '''
    def __init__(self, regs, sector_size, target, ap, name, dev_base, mem_base,
                 max_write_freq, otp_base, otp_len):
        Device.__init__(self, target, ap, dev_base, name, regs)
        Flash.__init__(self, mem_base, 2048, target.flash_size // 2048)

        self.max_write_freq = max_write_freq
        self.otp_base       = otp_base
        self.otp_len        = otp_len

        if self._read_optr() == 0:
            raise Exception('Unexpected OPTR=0, debug clocks may be disabled; '
                            'try using --srst')

    def _flash_unlocked(self):
        return UnlockedContextManager(self)

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
