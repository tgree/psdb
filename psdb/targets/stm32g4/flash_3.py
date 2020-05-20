# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Reg32, Reg32W
from .flash_base import FLASH_Base, UnlockedContextManager


class FLASH_3(FLASH_Base):
    '''
    Driver for the FLASH category 3 device on the STM32G4 series of MCUs:
        STM32G471
        STM32G473
        STM32G474
        STM32G483
        STM32G484
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
        optr = ap.read_32(dev_base + 0x20)
        print('OPTR: 0x%08X' % optr)
        if optr == 0:
            raise Exception('Unexpected OPTR=0, debug clocks may be disabled; '
                            'try using --srst')
        sector_size = 2048 if optr & (1<<22) else 4096

        FLASH_Base.__init__(self, FLASH_3.REGS, sector_size, target, ap, name,
                            dev_base, mem_base, max_write_freq, otp_base,
                            otp_len)

    def erase_sector(self, n, verbose=True):
        '''
        Erases the nth sector in flash.
        This checks if the flash banks are swapped and erases the appropriate
        sector if it needs to reverse the numbers.
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
            self._write_cr(0)

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
            pass

        return self.target.wait_reset_and_reprobe()
