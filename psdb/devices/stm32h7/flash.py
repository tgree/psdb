# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32, Reg32R, Reg32W
from ..flash import Flash


class FlashBank(Device):
    '''
    Driver for a single flash bank.
    '''
    REGS = [Reg32W('KEYR',      0x004, [('KEYR', 32)]),
            Reg32 ('CR',        0x00C, [('LOCK',       1),
                                        ('PG',         1),
                                        ('SER',        1),
                                        ('BER',        1),
                                        ('PSIZE',      2),
                                        ('FW',         1),
                                        ('START',      1),
                                        ('SNB',        3),
                                        ('',           4),
                                        ('CRC_EN',     1),
                                        ('EOPIE',      1),
                                        ('WRPERRIE',   1),
                                        ('PGSERRIE',   1),
                                        ('STRBERRIE',  1),
                                        ('',           1),
                                        ('INCERRIE',   1),
                                        ('OPERRIE',    1),
                                        ('RDPERRIE',   1),
                                        ('RDSERRIE',   1),
                                        ('SNECCERRIE', 1),
                                        ('DBECCERRIE', 1),
                                        ('CRCENDIE',   1),
                                        ('CRCRDERRIE', 1),
                                        ]),
            Reg32 ('SR',        0x010, [('BSY',        1),
                                        ('WBNE',       1),
                                        ('QW',         1),
                                        ('CRC_BUSY',   1),
                                        ('',          12),
                                        ('EOP',        1),
                                        ('WRPERR',     1),
                                        ('PGSERR',     1),
                                        ('STRBERR',    1),
                                        ('',           1),
                                        ('INCERR',     1),
                                        ('OPERR',      1),
                                        ('RDPERR',     1),
                                        ('RDSERR',     1),
                                        ('SNECCERR',   1),
                                        ('DBECCERR',   1),
                                        ('CRCEND',     1),
                                        ('CRCRDERR',   1),
                                        ]),
            Reg32W('CCR',       0x014, [('',            16),
                                        ('CLR_EOP',      1),
                                        ('CLR_WRPERR',   1),
                                        ('CLR_PGSERR',   1),
                                        ('CLR_STRBERR',  1),
                                        ('',             1),
                                        ('CLR_INCERR',   1),
                                        ('CLR_OPERR',    1),
                                        ('CLR_RDPERR',   1),
                                        ('CLR_RDSERR',   1),
                                        ('CLR_SNECCERR', 1),
                                        ('CLR_DBECCERR', 1),
                                        ('CLR_CRCEND',   1),
                                        ('CLR_CRCRDERR', 1),
                                        ]),
            Reg32 ('CRCCR',     0x050, [('CRC_SECT',     3),
                                        ('',             5),
                                        ('CRC_BY_SECT',  1),
                                        ('ADD_SECT',     1),
                                        ('CLEAN_SECT',   1),
                                        ('',             5),
                                        ('START_CRC',    1),
                                        ('CLEAN_CRC',    1),
                                        ('',             2),
                                        ('CRC_BURST',    2),
                                        ('ALL_BANK',     1),
                                        ]),
            Reg32 ('CRCSADDR',  0x054, [('',                2),
                                        ('CRC_START_ADDR', 18),
                                        ]),
            Reg32 ('CRCEADDR',  0x058, [('',                2),
                                        ('CRC_END_ADDR',   18),
                                        ]),
            Reg32R('ECC_FAR',   0x060, [('FAIL_ECC_ADDR', 15)]),
            ]

    def __init__(self, flash, bank_num, **kwargs):
        super(FlashBank, self).__init__(flash.target, flash.ap,
                                        flash.dev_base + 0x100*bank_num,
                                        '%s:BANK%u' % (flash.name, bank_num),
                                        FlashBank.REGS, **kwargs)

    def _clear_errors(self):
        self._CCR = 0x0FEF0000

    def _check_errors(self):
        v = self._SR.read()
        if v & 0x0FEE0000:
            raise Exception('Flash operation failed, FLASH_SR=0x%08X' % v)

    def _wait_prg_idle(self):
        while self._SR.read() & 7:
            pass

    def _pg_unlock(self):
        v = self._CR.read()
        if v & 1:
            self._KEYR = 0x45670123
            self._KEYR = 0xCDEF89AB
            v = self._CR.read()
            assert not (v & 1)
        if not (v & 2):
            self._CR = (v | 2)

        return self

    def _pg_lock(self):
        v = self._CR.read()
        self._CR = ((v & ~2) | 1)


class UnlockedContextManager(object):
    def __init__(self, bank):
        self.bank = bank

    def __enter__(self):
        self.bank._pg_unlock()
        return self

    def __exit__(self, type, value, traceback):
        self.bank._pg_lock()


class FLASH(Device, Flash):
    '''
    Driver for the FLASH device on the STM32H7xx series of MCUs.
    '''
    REGS = [Reg32 ('ACR',           0x000),
            Reg32W('KEYR1',         0x004),
            Reg32W('OPTKEYR',       0x008),
            Reg32 ('CR1',           0x00C),
            Reg32 ('SR1',           0x010),
            Reg32W('CCR1',          0x014),
            Reg32 ('OPTCR',         0x018),
            Reg32 ('OPTCCR',        0x024),
            Reg32 ('CRCCR1',        0x050),
            Reg32 ('CRCSADD1R',     0x054),
            Reg32 ('CRCEADD1R',     0x058),
            Reg32R('CRCDATAR',      0x05C),
            Reg32R('ECC_FA1R',      0x060),
            Reg32W('KEYR2',         0x104),
            Reg32 ('CR2',           0x10C),
            Reg32 ('SR2',           0x110),
            Reg32W('CCR2',          0x114),
            Reg32 ('CRCCR2',        0x150),
            Reg32 ('CRCSADD2R',     0x154),
            Reg32 ('CRCEADD2R',     0x158),
            Reg32R('ECC_FA2R',      0x160),
            ]

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq,
                 opt_regs, **kwargs):
        sector_size = 128*1024
        Device.__init__(self, target, ap, dev_base, name, FLASH.REGS + opt_regs,
                        **kwargs)
        Flash.__init__(self, mem_base, sector_size,
                       target.flash_size // sector_size)

        self.target          = target
        self.max_write_freq   = max_write_freq
        nbanks                = 1 if self.target.flash_size == 128*1024 else 2
        self.banks            = [FlashBank(self, i, **kwargs)
                                 for i in range(nbanks)]
        self.sectors_per_bank = self.nsectors // nbanks
        self.bank_size        = self.sector_size * self.sectors_per_bank

    def _flash_bank_unlocked(self, bank):
        return UnlockedContextManager(bank)

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

        bank = self.banks[n // self.sectors_per_bank]
        with self._flash_bank_unlocked(bank):
            bank._clear_errors()
            v  = bank._CR.read()
            v |= ((n % self.sectors_per_bank) << 8) | (1 << 7) | (1 << 2)
            bank._CR = v
            bank._wait_prg_idle()
            bank._check_errors()

    def read(self, addr, length):
        '''
        Reads a region from the flash.
        '''
        return self.ap.read_bulk(addr, length)

    def write(self, addr, data, verbose=True):
        '''
        Writes 32-byte lines of data to the flash.  The address must be
        32-byte aligned and the data to write must be a multiple of 32 bytes in
        length and should all be contained within one flash bank but may span
        multiple sectors.

        The target region to be written must be in the erased state.
        '''
        assert self.target.is_halted()
        if not data:
            return
        assert len(data) % 32 == 0
        assert addr % 32 == 0
        assert (addr & 0xFFF00000) == ((addr + len(data) - 1) & 0xFFF00000)
        assert self.mem_base <= addr
        assert addr + len(data) <= self.mem_base + self.flash_size

        if verbose:
            print('Flashing region [0x%08X - 0x%08X]...' % (
                    addr, addr + len(data) - 1))

        bank = self.banks[(addr - self.mem_base) // self.bank_size]
        with self._flash_bank_unlocked(bank):
            bank._clear_errors()
            self.ap.write_bulk(data, addr)
            bank._wait_prg_idle()
            bank._check_errors()
