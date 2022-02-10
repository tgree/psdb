# Copyright (c) 2022 by Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32
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
        if self.flash._NSCR.LOCK:
            self.flash._NSKEYR = 0x45670123
            self.flash._NSKEYR = 0xCDEF89AB
            assert not self.flash._NSCR.LOCK

    def __exit__(self, type, value, traceback):
        self.flash._NSCR.LOCK = 1


class UnlockedOptionsContextManager(object):
    def __init__(self, flash):
        self.flash = flash

    def __enter__(self):
        if self.flash._NSCR.OPTLOCK:
            assert not self.flash._NSCR.LOCK
            self.flash._OPTKEYR = 0x08192A3B
            self.flash._OPTKEYR = 0x4C5D6E7F
            assert not self.flash._NSCR.OPTLOCK

    def __exit__(self, type, value, traceback):
        self.flash._NSCR.OPTLOCK = 1


class FLASH(Device, Flash):
    '''
    Driver for the FLASH device on the STM32U585 series of MCUs.
    '''
    REGS = [AReg32('ACR',           0x000, [('LATENCY',         0, 3),
                                            ('PRFTEN',          8),
                                            ('LPM',             11),
                                            ('PDREQ1',          12),
                                            ('PDREQ2',          13),
                                            ('SLEEP_PD',        14),
                                            ]),
            AReg32('NSKEYR',        0x008),
            AReg32('SECKEYR',       0x00C),
            AReg32('OPTKEYR',       0x010),
            AReg32('PDKEY1R',       0x018),
            AReg32('PDKEY2R',       0x01C),
            AReg32('NSSR',          0x020, [('EOP',             0),
                                            ('OPERR',           1),
                                            ('PROGERR',         3),
                                            ('WRPERR',          4),
                                            ('PGAERR',          5),
                                            ('SIZERR',          6),
                                            ('PGSERR',          7),
                                            ('OPTWERR',         13),
                                            ('BSY',             16),
                                            ('WDW',             17),
                                            ('OEM1LOCK',        18),
                                            ('OEM2LOCK',        19),
                                            ('PD1',             20),
                                            ('PD2',             21),
                                            ]),
            AReg32('SECSR',         0x024, [('EOP',             0),
                                            ('OPERR',           1),
                                            ('PROGERR',         3),
                                            ('WRPERR',          4),
                                            ('PGAERR',          5),
                                            ('SIZERR',          6),
                                            ('PGSERR',          7),
                                            ('BSY',             16),
                                            ('WDW',             17),
                                            ]),
            AReg32('NSCR',          0x028, [('PG',              0),
                                            ('PER',             1),
                                            ('MER1',            2),
                                            ('PNB',             3, 9),
                                            ('BKER',            11),
                                            ('BWR',             14),
                                            ('MER2',            15),
                                            ('STRT',            16),
                                            ('OPTSTRT',         17),
                                            ('EOPIE',           24),
                                            ('ERRIE',           25),
                                            ('OBL_LAUNCH',      27),
                                            ('OPTLOCK',         30),
                                            ('LOCK',            31),
                                            ]),
            AReg32('SECCR',         0x02C, [('PG',              0),
                                            ('PER',             1),
                                            ('MER1',            2),
                                            ('PNB',             3, 9),
                                            ('BKER',            11),
                                            ('BWR',             14),
                                            ('MER2',            15),
                                            ('STRT',            16),
                                            ('EOPIE',           24),
                                            ('ERRIE',           25),
                                            ('INV',             29),
                                            ('LOCK',            31),
                                            ]),
            AReg32('ECCR',          0x030, [('ADDR_ECC',        0, 19),
                                            ('BK_ECC',          21),
                                            ('SYSF_ECC',        22),
                                            ('ECCIE',           24),
                                            ('ECCC',            30),
                                            ('ECCD',            31),
                                            ]),
            AReg32('OPSR',          0x034, [('ADDR_OP',         0,  19),
                                            ('BK_OP',           21),
                                            ('SYSF_OP',         22),
                                            ('CODE_OP',         29, 31),
                                            ]),
            AReg32('OPTR',          0x040, [('RDP',             0, 7),
                                            ('BOR_LEV',         8, 10),
                                            ('nRST_STOP',       12),
                                            ('nRST_STDBY',      13),
                                            ('nRST_SHDW',       14),
                                            ('SRAM1345_RST',    15),
                                            ('IWDG_SW',         16),
                                            ('IWDG_STOP',       17),
                                            ('IWDG_STDBY',      18),
                                            ('WWDG_SW',         19),
                                            ('SWAP_BANK',       20),
                                            ('DUALBANK',        21),
                                            ('BKPRAM_ECC',      22),
                                            ('SRAM3_ECC',       23),
                                            ('SRAM2_ECC',       24),
                                            ('SRAM2_RST',       25),
                                            ('nSWBOOT0',        26),
                                            ('nBOOT0',          27),
                                            ('PA15_PUPEN',      28),
                                            ('IO_VDD_HSLV',     29),
                                            ('IO_VDDIO2_HSLV',  30),
                                            ('TZEN',            31),
                                            ]),
            AReg32('NSBOOTADD0R',   0x044),
            AReg32('NSBOOTADD1R',   0x048),
            AReg32('SECBOOTADD0R',  0x04C, [('BOOT_LOCK',       0),
                                            ('SECBOOTADD0',     7, 31),
                                            ]),
            AReg32('SECWM1R1',      0x050, [('SECWM1_PSTRT',    0,  6),
                                            ('SECWM1_PEND',     16, 22),
                                            ]),
            AReg32('SECWM1R2',      0x054, [('HDP1_PEND',       16, 22),
                                            ('HDP1EN',          31),
                                            ]),
            AReg32('WRP1AR',        0x058, [('WRP1A_PSTRT',     0,  6),
                                            ('WRP1A_PEND',      16, 22),
                                            ('UNLOCK',          31),
                                            ]),
            AReg32('WRP1BR',        0x05C, [('WRP1B_PSTRT',     0,  6),
                                            ('WRP1B_PEND',      16, 22),
                                            ('UNLOCK',          31),
                                            ]),
            AReg32('SECWM2R1',      0x060, [('SECWM2_PSTRT',    0,  6),
                                            ('SECWM2_PEND',     16, 22),
                                            ]),
            AReg32('SECWM2R2',      0x064, [('HDP2_PEND',       16, 22),
                                            ('HDP2EN',          31),
                                            ]),
            AReg32('WRP2AR',        0x068, [('WRP2A_PSTRT',     0,  6),
                                            ('WRP2A_PEND',      16, 22),
                                            ('UNLOCK',          31),
                                            ]),
            AReg32('WRP2BR',        0x06C, [('WRP2B_PSTRT',     0,  6),
                                            ('WRP2B_PEND',      16, 22),
                                            ('UNLOCK',          31),
                                            ]),
            AReg32('OEM1KEYR1',     0x070),
            AReg32('OEM1KEYR2',     0x074),
            AReg32('OEM2KEYR1',     0x078),
            AReg32('OEM2KEYR2',     0x07C),
            AReg32('SECBB1R0',      0x080),
            AReg32('SECBB1R1',      0x084),
            AReg32('SECBB1R2',      0x088),
            AReg32('SECBB1R3',      0x08C),
            AReg32('SECBB2R0',      0x0A0),
            AReg32('SECBB2R1',      0x0A4),
            AReg32('SECBB2R2',      0x0A8),
            AReg32('SECBB2R3',      0x0AC),
            AReg32('SECHDPCR',      0x0C0, [('HDP1_ACCDIS',     0),
                                            ('HDP2_ACCDIS',     1),
                                            ]),
            AReg32('PRIVCFGR',      0x0C4, [('SPRIV',           0),
                                            ('NSPRIV',          1),
                                            ]),
            AReg32('PRIVBB1R0',     0x0D0),
            AReg32('PRIVBB1R1',     0x0D4),
            AReg32('PRIVBB1R2',     0x0D8),
            AReg32('PRIVBB1R3',     0x0DC),
            AReg32('PRIVBB2R0',     0x0F0),
            AReg32('PRIVBB2R1',     0x0F4),
            AReg32('PRIVBB2R2',     0x0F8),
            AReg32('PRIVBB2R3',     0x0FC),
            ]

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq,
                 otp_base, otp_len, **kwargs):
        Device.__init__(self, target, ap, dev_base, name, FLASH.REGS, **kwargs)
        Flash.__init__(self, mem_base, 8192, target.flash_size // 8192)

        self.target         = target
        self.max_write_freq = max_write_freq
        self.otp_base       = otp_base
        self.otp_len        = otp_len

    def _flash_unlocked(self):
        return UnlockedContextManager(self)

    def _options_unlocked(self):
        return UnlockedOptionsContextManager(self)

    def _clear_errors(self):
        self._NSSR = self._NSSR

    def _check_errors(self):
        v = self._NSSR.read()
        if v & 0x000020FA:
            raise Exception('Flash operation failed, FLASH_NSSR=0x%08X' % v)

    def _wait_bsy_clear(self):
        # Wait for both BSY and WDW to be clear simultaneously.
        v = self._NSSR.read()
        while v & 0x00030000:
            v = self._NSSR.read()

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

        # In dual-bank mode, do the right thing if the banks are swapped.  Note
        # that the U5 does not suffer from the FB_MODE/BFB2 synchronization
        # issues that the G4 does; the SWAP_BANK setting is honored by the MCU
        # before the reset vector is fetched rather than relying on boot ROM
        # code to flip an FB_MODE-like bit, so all we have to do is invert the
        # BKER bit if SWAP_BANK is set.
        if self._OPTR.DUALBANK or self.nsectors == 256:
            bank_swap    = bool(self._OPTR.SWAP_BANK)
            bank_sectors = self.nsectors // 2
            bker         = ((n >= bank_sectors) ^ bank_swap)
            n            = (n % bank_sectors)
        else:
            bker = 0

        with self._flash_unlocked():
            self._clear_errors()
            self._NSCR = ((n << 3) | (1 << 1))
            try:
                self._NSCR = ((1 << 16) | (bker << 11) | (n << 3) | (1 << 1))
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
            self._NSCR = (1 << 0)
            try:
                self.ap.write_bulk(data, addr)
                self._wait_bsy_clear()
                self._check_errors()
            finally:
                self._NSCR = 0

    def _flash_options(self, new_optr, new_nsbootadd0, new_nsbootadd1,
                       new_secbootadd0, verbose=True):
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
                if new_nsbootadd0 is not None:
                    self._NSBOOTADD0R = new_nsbootadd0
                if new_nsbootadd1 is not None:
                    self._NSBOOTADD1R = new_nsbootadd1
                if new_secbootadd0 is not None:
                    self._SECBOOTADD0R = new_secbootadd0
                self._clear_errors()
                self._NSCR = (1 << 17)
                self._wait_bsy_clear()
                self._check_errors()

    def _trigger_obl_launch(self, **kwargs):
        '''
        Set OBL_LAUNCH to trigger an uncatchable reset of the device using the
        new options.  This reset triggers a disconnect of the debug probe, and
        the current target object becomes unusable.  A target reprobe() is
        required if it is desired to reconnect after the reset completes.
        '''
        UnlockedContextManager(self).__enter__()
        UnlockedOptionsContextManager(self).__enter__()

        # Set OBL_LAUNCH to trigger a reset and load of the new settings.  This
        # causes an exception with the XDS110 and the ST-Link, so catch it and
        # exit cleanly.
        try:
            self._NSCR = (1 << 27)
        except Exception:
            pass

        self.target.wait_reset()

    def get_options_reg(self):
        '''Returns the contents of the options register.'''
        return self._OPTR.read()

    def get_options(self):
        '''
        Returns the set of options currently visible in the OPTR register.  The
        OPTR register is a shadow of the configured options; when you read this
        register it returns the currently-active set of options and NOT the set
        of options that an OBL reboot would make active.
        '''
        optr = self._OPTR.read()
        options = {
            name.lower() : ((optr >> shift) & ((1 << width) - 1))
            for name, (width, shift) in self._OPTR.reg.fields_map.items()
        }
        options['nsbootadd0'] = self._NSBOOTADD0R.read()
        options['nsbootadd1'] = self._NSBOOTADD1R.read()
        options['secbootadd0'] = self._SECBOOTADD0R.read()
        return options

    def set_options_no_connect(self, options, verbose=True):
        '''
        This sets the specified option bits in the OPTR register and then
        triggers an option-byte load reset of the MCU.  The MCU is not re-
        probed and the previous target object becomes unusable.  This is
        useful for setting the options as the last step before restarting the
        MCU to let it run autonomously.
        '''
        nsbootadd0 = options.get('nsbootadd0')
        if nsbootadd0 is not None:
            del options['nsbootadd0']
        nsbootadd1 = options.get('nsbootadd1')
        if nsbootadd1 is not None:
            del options['nsbootadd1']
        secbootadd0 = options.get('secbootadd0')
        if secbootadd0 is not None:
            del options['secbootadd0']

        optr = self._OPTR.read()
        for name, (width, shift) in self._OPTR.reg.fields_map.items():
            value = options.get(name.lower(), None)
            if value is None:
                continue

            assert value <= ((1 << width) - 1)
            optr &= ~(((1 << width) - 1) << shift)
            optr |= (value << shift)
            del options[name.lower()]

        if options:
            raise Exception('Invalid options: %s' % options)

        self._flash_options(optr, nsbootadd0, nsbootadd1, secbootadd0,
                            verbose=verbose)
        self._trigger_obl_launch(verbose=verbose)

    def set_options(self, options, verbose=True, connect_under_reset=False):
        '''
        This sets the specified option bits in the OPTR register and then
        triggers an option-byte load reset of the MCU.  When the MCU comes back
        up, the new options will be in effect.  This reset invalidates the
        probe's connection to the target, so the correct idiom for use is:

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
