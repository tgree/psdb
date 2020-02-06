# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32, Reg32W
from ..flash import Flash


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
            Reg32 ('OPTR',          0x020),
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

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq):
        Device.__init__(self, target, ap, dev_base, name, FLASH.REGS)
        optr        = self._read_optr()
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
        The sector is verified to be erased before returning.
        '''
        assert 0 <= n and n < self.nsectors

        addr = self.mem_base + n * self.sector_size
        if verbose:
            print('Erasing sector [0x%08X - 0x%08X]...' % (
                    addr, addr + self.sector_size - 1))

        with self._flash_unlocked():
            self._clear_errors()
            self._write_cr((n << 3) | (1 << 1))
            self._write_cr((1 << 16) | (n << 3) | (1 << 1))
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
        assert self.mem_base <= addr
        assert addr + len(data) <= self.mem_base + self.flash_size

        if verbose:
            print('Flashing region [0x%08X - 0x%08X]...' % (
                    addr, addr + len(data) - 1))

        with self._flash_unlocked():
            self._clear_errors()
            self._write_cr(1 << 0)
            self.ap.write_bulk(data, addr)
            self._wait_bsy_clear()
            self._check_errors()
