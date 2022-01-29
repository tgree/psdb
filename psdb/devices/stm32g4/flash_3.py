# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Reg32, Reg32W, AReg32
from ..stm32 import flash_type1


class FLASH_3(flash_type1.FLASH):
    '''
    Driver for the FLASH category 3 device on the STM32G4 series of MCUs:
        STM32G471
        STM32G473
        STM32G474
        STM32G483
        STM32G484
    '''
    REGS = [AReg32('ACR',           0x000, [('LATENCY',     0, 3),
                                            ('PRFTEN',      8),
                                            ('ICEN',        9),
                                            ('DCEN',        10),
                                            ('ICRST',       11),
                                            ('DCRST',       12),
                                            ('RUN_PD',      13),
                                            ('SLEEP_PD',    14),
                                            ('DBG_SWEN',    18),
                                            ]),
            Reg32 ('PDKEYR',        0x004),
            Reg32W('KEYR',          0x008),
            Reg32W('OPTKEYR',       0x00C),
            Reg32 ('SR',            0x010, [('EOP',         1),
                                            ('OPERR',       1),
                                            ('',            1),
                                            ('PROGERR',     1),
                                            ('WRPERR',      1),
                                            ('PGAERR',      1),
                                            ('SIZERR',      1),
                                            ('PGSERR',      1),
                                            ('MISSERR',     1),
                                            ('FASTERR',     1),
                                            ('',            4),
                                            ('RDERR',       1),
                                            ('OPTVERR',     1),
                                            ('BSY',         1),
                                            ]),
            Reg32 ('CR',            0x014, [('PG',          1),
                                            ('PER',         1),
                                            ('MER1',        1),
                                            ('PNB',         7),
                                            ('',            1),
                                            ('BKER',        1),
                                            ('',            3),
                                            ('MER2',        1),
                                            ('STRT',        1),
                                            ('OPTSTR',      1),
                                            ('FSTPG',       1),
                                            ('',            5),
                                            ('EOPIE',       1),
                                            ('ERRIE',       1),
                                            ('RDERRIE',     1),
                                            ('OBL_LAUNCH',  1),
                                            ('SEC_PROT1',   1),
                                            ('SEC_PROT2',   1),
                                            ('OPTLOCK',     1),
                                            ('LOCK',        1),
                                            ]),
            AReg32('ECCR',          0x018, [('ADDR_ECC',    0, 18),
                                            ('BK_ECC',      21),
                                            ('SYSF_ECC',    22),
                                            ('ECCCIE',      24),
                                            ('ECCC2',       28),
                                            ('ECCD2',       29),
                                            ('ECCC',        30),
                                            ('ECCD',        31),
                                            ]),
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
                 otp_base, otp_len, **kwargs):
        optr = ap.read_32(dev_base + 0x20)
        if optr == 0:
            raise Exception('Unexpected OPTR=0, debug clocks may be disabled; '
                            'try using --srst')
        sector_size = 2048 if optr & (1<<22) else 4096

        super(FLASH_3, self).__init__(target, FLASH_3.REGS, sector_size, ap,
                                      name, dev_base, mem_base, max_write_freq,
                                      otp_base, otp_len, **kwargs)

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
            bker = (((n >= 128) ^ self.target.fb_mode) << 11)
            n    = (n % 128)
        else:
            bker = 0

        with self._flash_unlocked():
            self._clear_errors()
            self._CR = ((n << 3) | (1 << 1) | bker)
            self._CR = ((1 << 16) | (n << 3) | (1 << 1) | bker)
            self._wait_bsy_clear()
            self._check_errors()
            self._CR = 0

    def swap_banks_and_reset_no_connect(self):
        '''
        Swap the flash banks in dual-bank mode.  This also triggers a reset,
        which invalidates the probe's connection to the target.  The target is
        not halted and the target object becomes unusable.
        '''
        options = self.get_options()
        self.set_options_no_connect({'bfb2' : (options['bfb2'] ^ 1)})
