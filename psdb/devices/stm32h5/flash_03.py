# Copyright (c) 2022 by Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32
from ..flash import Flash


def block_in_region(addr, size, region_base, region_len):
    return ((region_base <= addr) and
            (addr + size <= region_base + region_len))


def write_in_region(addr, data, region_base, region_len):
    return block_in_region(addr, len(data), region_base, region_len)


class UnlockedContextManager:
    def __init__(self, flash):
        self.flash = flash

    def __enter__(self):
        if self.flash._NSCR.LOCK:
            self.flash._NSKEYR = 0x45670123
            self.flash._NSKEYR = 0xCDEF89AB
            assert not self.flash._NSCR.LOCK

    def __exit__(self, _type, value, traceback):
        self.flash._NSCR.LOCK = 1


class UnlockedOptionsContextManager:
    def __init__(self, flash):
        self.flash = flash

    def __enter__(self):
        if self.flash._OPTCR.OPTLOCK:
            self.flash._OPTKEYR = 0x08192A3B
            self.flash._OPTKEYR = 0x4C5D6E7F
            assert not self.flash._OPTCR.OPTLOCK

    def __exit__(self, _type, value, traceback):
        self.flash._OPTCR.OPTLOCK = 1


class FLASH_03(Device, Flash):
    '''
    Driver for the FLASH device on the STM32H503 series of MCUs.
    '''
    REGS = [AReg32('ACR',           0x000, [('LATENCY',             0,  3),
                                            ('WRHIGHFREQ',          4,  5),
                                            ('PRFTEN',              8),
                                            ]),
            AReg32('NSKEYR',        0x004),
            AReg32('OPTKEYR',       0x00C),
            AReg32('OPSR',          0x018, [('ADDR_OP',             0,  19),
                                            ('BK_OP',               22),
                                            ('SYSF_OP',             23),
                                            ('OTP_OP',              24),
                                            ('CODE_OP',             29, 31),
                                            ]),
            AReg32('OPTCR',         0x01C, [('OPTLOCK',             0),
                                            ('OPTSTRT',             1),
                                            ('SWAP_BANK',           31),
                                            ]),
            AReg32('NSSR',          0x020, [('BSY',                 0),
                                            ('WBNE',                1),
                                            ('DBNE',                3),
                                            ('EOP',                 16),
                                            ('WRPERR',              17),
                                            ('PGSERR',              18),
                                            ('STRBERR',             19),
                                            ('INCERR',              20),
                                            ('OPTCHANGEERR',        23),
                                            ]),
            AReg32('NSCR',          0x028, [('LOCK',                0),
                                            ('PG',                  1),
                                            ('SER',                 2),
                                            ('BER',                 3),
                                            ('FW',                  4),
                                            ('STRT',                5),
                                            ('SNB',                 6,  8),
                                            ('MER',                 15),
                                            ('EOPIE',               16),
                                            ('WRPERRIE',            17),
                                            ('PGSERRIE',            18),
                                            ('STRBERRIE',           19),
                                            ('INCERRIE',            20),
                                            ('OPTCHANGEERRIE',      23),
                                            ('BKSEL',               31),
                                            ]),
            AReg32('NSCCR',         0x030, [('CLR_EOP',             16),
                                            ('CLR_WRPERR',          17),
                                            ('CLR_PGSERR',          18),
                                            ('CLR_STRBERR',         19),
                                            ('CLR_INCERR',          20),
                                            ('CLR_OPTCHANGEERR',    23),
                                            ]),
            AReg32('PRIVCFGR',      0x03C, [('NSPRIV',              1),
                                            ]),
            AReg32('HDPEXTR',       0x048, [('HDP1_EXT',            0,  2),
                                            ('HDP2_EXT',            16, 18),
                                            ]),
            AReg32('OPTSR_CUR',     0x050, [('BOR_LEV',             0,  1),
                                            ('BORH_EN',             2),
                                            ('IWDG_SW',             3),
                                            ('WWDG_SW',             4),
                                            ('NRST_STOP',           6),
                                            ('NRST_STDBY',          7),
                                            ('PRODUCT_STATE',       8,  15),
                                            ('IO_VDD_HSLV',         16),
                                            ('IO_VDDIO2_HSLV',      17),
                                            ('IWDG_STOP',           20),
                                            ('IWDG_STDBY',          21),
                                            ('SWAP_BANK',           31),
                                            ]),
            AReg32('OPTSR_PRG',     0x054, [('BOR_LEV',             0,  1),
                                            ('BORH_EN',             2),
                                            ('IWDG_SW',             3),
                                            ('WWDG_SW',             4),
                                            ('NRST_STOP',           6),
                                            ('NRST_STDBY',          7),
                                            ('PRODUCT_STATE',       8,  15),
                                            ('IO_VDD_HSLV',         16),
                                            ('IO_VDDIO2_HSLV',      17),
                                            ('IWDG_STOP',           20),
                                            ('IWDG_STDBY',          21),
                                            ('SWAP_BANK',           31),
                                            ]),
            AReg32('OPTSR2_CUR',    0x070, [('SRAM2_RST',           3),
                                            ('BKPRAM_ECC',          4),
                                            ('SRAM2_ECC',           6),
                                            ('SRAM1_RST',           9),
                                            ('SRAM1_ECC',           10),
                                            ]),
            AReg32('OPTSR2_PRG',    0x074, [('SRAM2_RST',           3),
                                            ('BKPRAM_ECC',          4),
                                            ('SRAM2_ECC',           6),
                                            ('SRAM1_RST',           9),
                                            ('SRAM1_ECC',           10),
                                            ]),
            AReg32('NSBOOTR_CUR',   0x080, [('NSBOOT_LOCK',         0,  7),
                                            ('NSBOOTADD',           8,  31),
                                            ]),
            AReg32('NSBOOTR_PRG',   0x084, [('NSBOOT_LOCK',         0,  7),
                                            ('NSBOOTADD',           8,  31),
                                            ]),
            AReg32('OPTBLR_CUR',    0x090, [('LOCKBL',              0,  31),
                                            ]),
            AReg32('OPTBLR_PRG',    0x094, [('LOCKBL',              0,  31),
                                            ]),
            AReg32('PRIVBB1R1',     0x0C0, [('PRIVBB1',             0,  7),
                                            ]),
            AReg32('WRP1R_CUR',     0x0E8, [('WRPSG1',              0,  7),
                                            ]),
            AReg32('WRP1R_PRG',     0x0EC, [('WRPSG1',              0,  7),
                                            ]),
            AReg32('HDP1R_CUR',     0x0F8, [('HDP1_STRT',           0,  2),
                                            ('HDP1_END',            16, 18),
                                            ]),
            AReg32('HDP1R_PRG',     0x0FC, [('HDP1_STRT',           0,  2),
                                            ('HDP1_END',            16, 18),
                                            ]),
            AReg32('ECCCORR',       0x100, [('ADDR_ECC',            0,  15),
                                            ('BK_ECC',              22),
                                            ('SYSF_ECC',            23),
                                            ('OTP_ECC',             24),
                                            ('ECCCIE',              25),
                                            ('ECCC',                30),
                                            ]),
            AReg32('ECCDETR',       0x104, [('ADDR_ECC',            0,  15),
                                            ('BK_ECC',              22),
                                            ('SYSF_ECC',            23),
                                            ('OTP_ECC',             24),
                                            ('ECCD',                31),
                                            ]),
            AReg32('ECCDR',         0x108, [('DATA_ECC',            0,  15),
                                            ]),
            AReg32('PRIVBB2R1',     0x1C0, [('PRIVBB2',             0,  7),
                                            ]),
            AReg32('WRP2R_CUR',     0x1E8, [('WRPSG2',              0,  7),
                                            ]),
            AReg32('WRP2R_PRG',     0x1EC, [('WRPSG2',              0,  7),
                                            ]),
            AReg32('HDP2R_CUR',     0x1F8, [('HDP2_STRT',           0,  2),
                                            ('HDP2_END',            16, 18),
                                            ]),
            AReg32('HDP2R_PRG',     0x1FC, [('HDP2_STRT',           0,  2),
                                            ('HDP2_END',            16, 18),
                                            ]),
            ]

    def __init__(self, target, ap, name, dev_base, mem_base,
                 max_nowait_write_freq, otp_base, otp_len, **kwargs):
        Device.__init__(self, target, ap, dev_base, name, FLASH_03.REGS,
                        **kwargs)
        Flash.__init__(self, mem_base, 8192, target.flash_size // 8192,
                       max_nowait_write_freq)

        self.target   = target
        self.otp_base = otp_base
        self.otp_len  = otp_len

    def _flash_unlocked(self):
        return UnlockedContextManager(self)

    def _options_unlocked(self):
        return UnlockedOptionsContextManager(self)

    def _clear_errors(self):
        self._NSCCR = 0x009F0000
        self._ECCCORR = (1 << 30)
        self._ECCDETR = (1 << 31)

    def _check_errors(self):
        v = self._NSSR.read()
        if v & 0x009E0000:
            raise Exception('Flash operation failed, FLASH_NSSR=0x%08X' % v)
        v = self._ECCCORR.read()
        if v & (1 << 30):
            raise Exception('Flash single-ECC corrected, '
                            'FLASH_ECCCORR=0x%08X' % v)
        v = self._ECCDETR.read()
        if v & (1 << 31):
            raise Exception('Flash double-ECC detected, '
                            'FLASH_ECCDETR=0x%08X' % v)

    def _wait_bsy_clear(self):
        # Wait for both BSY and WBNE to be clear simultaneously.
        v = self._NSSR.read()
        while v & 0x00000003:
            v = self._NSSR.read()

    def erase_sector(self, n, verbose=True):
        '''
        Erases the nth sector in flash.
        '''
        assert 0 <= n < self.nsectors

        addr = self.mem_base + n * self.sector_size
        if verbose:
            print('Erasing sector [0x%08X - 0x%08X]...' % (
                    addr, addr + self.sector_size - 1))

        # Do the right thing if the banks are swapped.
        bank_swap    = bool(self._OPTCR.SWAP_BANK)
        bank_sectors = self.nsectors // 2
        bksel        = ((n >= bank_sectors) ^ bank_swap)
        n            = (n % bank_sectors)

        with self._flash_unlocked():
            self._clear_errors()
            self._NSCR = ((bksel << 31) | (n << 6) | (1 << 2))
            try:
                self._NSCR = ((1 << 5) | (bksel << 31) | (n << 6) | (1 << 2))
                self._wait_bsy_clear()
                self._check_errors()
            finally:
                self._NSCR = 0

    def read(self, addr, length):
        '''
        Reads a region from the flash.
        '''
        return self.ap.read_bulk(addr, length)

    def write(self, addr, data, verbose=True):
        '''
        Writes 16-byte lines of data to the flash.  The address must be
        16-byte aligned and the data to write must be a multiple of 16 bytes in
        length.

        The target region to be written must be in the erased state.
        '''
        assert self.target.is_halted()
        if not data:
            return
        assert len(data) % 16 == 0
        assert addr % 16 == 0
        assert (write_in_region(addr, data, self.mem_base, self.flash_size) or
                write_in_region(addr, data, self.otp_base, self.otp_len))

        if verbose:
            print('Flashing region [0x%08X - 0x%08X]...' % (
                    addr, addr + len(data) - 1))

        with self._flash_unlocked():
            self._clear_errors()
            self._NSCR = (1 << 1)
            try:
                self.ap.write_bulk(data, addr)
                self._wait_bsy_clear()
                self._check_errors()
            finally:
                self._NSCR = 0

    def read_otp(self, offset, size):
        '''
        Reads a block of one-time-programmable memory.
        '''
        assert offset + size <= self.otp_len
        addr = self.otp_base + offset
        return self.ap.read_bulk(addr, size)

    def is_otp_writeable(self, offset, size,
                         verbose=True):  # pylint: disable=W0613
        '''
        Determines if the selected region of one-time-programmable memory is
        still writeable.  Flash memory ECC is per 128-bit (16-byte) quad-word;
        if any byte if the quad-word has been written then the ECC has been
        saved and further writes are not allowed.  It is impossible to tell if
        a quad-word has been written already with all-0xFF, but we assume it
        has not if the full quad-word is all-0xFF.
        '''
        assert size > 0
        assert offset + size <= self.otp_len
        first_word = int(offset // 16)
        last_word  = int((offset + size - 1) // 16)
        offset     = first_word * 16
        size       = (last_word - first_word + 1) * 16
        return self.read_otp(offset, size) == (b'\xFF'*size)

    def write_otp(self, offset, data, verbose=True):  # pylint: disable=W0613
        '''
        Writes 16-byte lines of data to the one-time-programmable area in flash.
        The address must be 16-byte aligned and the data to write must be a
        multiple of 16 bytes in length.

        The target region to be written must be in the erased state (every 16-
        byte quad-word must be exactly all-0xFF - if any of the 128 bits has
        already been written, the entire quad-word is no longer writeable).
        '''
        assert self.is_otp_writeable(offset, len(data))
        self.write(self.otp_base + offset, data)

    def _flash_options(self, new_optsr1, new_optsr2, new_nsbootr, verbose=True):
        '''
        Records the current option values in flash, but doesn't reset the MCU
        so they won't yet take effect or even read back from the flash
        registers.
        '''
        assert self.target.is_halted()
        old_optsr1 = self._OPTSR_CUR.read()
        old_optsr2 = self._OPTSR2_CUR.read()
        old_nsbootr = self._NSBOOTR_CUR.read()
        if verbose:
            if new_nsbootr is not None:
                print('Flashing options (Old OPTSR=0x%08X, OPTSR2=0x%08X, '
                      'NSBOOTR=0x%08X New OPTR=0x%08X, OPTSR2=0x%08X, '
                      'NSBOOTR=0x%08X)'
                      % (old_optsr1, old_optsr2, old_nsbootr, new_optsr1,
                         new_optsr2, new_nsbootr))
            else:
                print('Flashing options (Old OPTSR=0x%08X, OPTSR2=0x%08X, '
                      'New OPTR=0x%08X, OPTSR2=0x%08X)'
                      % (old_optsr1, old_optsr2, new_optsr1, new_optsr2))
        with self._options_unlocked():
            self._OPTSR_PRG = new_optsr1
            self._OPTSR2_PRG = new_optsr2
            if new_nsbootr is not None:
                self._NSBOOTR_PRG = new_nsbootr
            self._clear_errors()
            self._OPTCR = (1 << 1)
            self._wait_bsy_clear()
            self._check_errors()

    def _trigger_obl_launch(self, **kwargs):  # pylint: disable=W0613
        '''
        The STM32H503 automatically loads the new options bytes after the
        OPTSTRT process completes, unlike on other devices.  However, for
        changes to e.g. NSBOOTR or SWAP_BANK, we really need to reset the
        device now.
        '''
        c = self.ap.db.cpus[0]
        c.enable_reset_vector_catch()
        c.trigger_local_reset()
        c.inval_halted_state()
        while not c.is_halted():
            pass
        c.disable_reset_vector_catch()

    def get_options_reg(self):
        '''Returns the contents of the options register.'''
        return ((self._OPTSR_CUR.read() << 32) | self._OPTSR2_CUR.read())

    def get_options(self):
        '''
        Returns the set of options currently visible in the OPTR register.  The
        OPTR register is a shadow of the configured options; when you read this
        register it returns the currently-active set of options and NOT the set
        of options that an OBL reboot would make active.
        '''
        optsr1 = self._OPTSR_CUR.read()
        options1 = {
            name.lower() : ((optsr1 >> shift) & ((1 << width) - 1))
            for name, (width, shift) in self._OPTSR_CUR.reg.fields_map.items()
        }

        optsr2 = self._OPTSR2_CUR.read()
        options2 = {
            name.lower() : ((optsr2 >> shift) & ((1 << width) - 1))
            for name, (width, shift) in self._OPTSR2_CUR.reg.fields_map.items()
        }

        options = {
            **options1,
            **options2,
            'nsbootr' : self._NSBOOTR_CUR.read(),
            }
        return options

    def set_options_no_connect(self, options, verbose=True):
        '''
        This sets the specified option bits in the OPTR register and then
        triggers an option-byte load reset of the MCU.  The MCU is not re-
        probed and the previous target object becomes unusable.  This is
        useful for setting the options as the last step before restarting the
        MCU to let it run autonomously.
        '''
        nsbootr = options.get('nsbootr')
        if nsbootr is not None:
            del options['nsbootr']

        optsr1 = self._OPTSR_CUR.read()
        for name, (width, shift) in self._OPTSR_PRG.reg.fields_map.items():
            value = options.get(name.lower(), None)
            if value is None:
                continue

            assert value <= ((1 << width) - 1)
            optsr1 &= ~(((1 << width) - 1) << shift)
            optsr1 |= (value << shift)
            del options[name.lower()]

        optsr2 = self._OPTSR2_CUR.read()
        for name, (width, shift) in self._OPTSR2_PRG.reg.fields_map.items():
            value = options.get(name.lower(), None)
            if value is None:
                continue

            assert value <= ((1 << width) - 1)
            optsr2 &= ~(((1 << width) - 1) << shift)
            optsr2 |= (value << shift)
            del options[name.lower()]

        if options:
            raise Exception('Invalid options: %s' % options)

        self._flash_options(optsr1, optsr2, nsbootr, verbose=verbose)
        self._trigger_obl_launch(verbose=verbose)

    def set_options(self, options, verbose=True, connect_under_reset=False):
        '''
        This sets the specified option bits in the OPTR register and then
        triggers a reset of the MCU with reset vector catching enabled.  When
        the MCU comes back up, the new options will be in effect.  This reset
        does not invalidate the probe's connection to the target, but for
        compatibility with other targets the following idiom is still
        supported:

            target = target.flash.set_options({...})
        '''
        self.set_options_no_connect(options, verbose=verbose)
        return self.target.reprobe(verbose=verbose,
                                   connect_under_reset=connect_under_reset)

    def swap_banks_and_reset_no_connect(self):
        '''
        Swap the flash banks in dual-bank mode.  This also triggers a reset,
        which invalidates the probe's connection to the target.  The target is
        not halted and the target object becomes unusable.
        '''
        options = self.get_options()
        self.set_options_no_connect({'swap_bank' : (options['swap_bank'] ^ 1)})
