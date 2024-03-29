# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Reg32, Reg32W
from ..stm32 import flash_type1


class FLASH_2(flash_type1.FLASH):
    '''
    Driver for the FLASH category 2 device on the STM32G4 series of MCUs:
        STM32G431
        STM32G441
    '''
    REGS = [Reg32 ('ACR',           0x000),
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
                                            ('',            6),
                                            ('STRT',        1),
                                            ('OPTSTR',      1),
                                            ('FSTPG',       1),
                                            ('',            5),
                                            ('EOPIE',       1),
                                            ('ERRIE',       1),
                                            ('RDERRIE',     1),
                                            ('OBL_LAUNCH',  1),
                                            ('SEC_PROT1',   1),
                                            ('',            1),
                                            ('OPTLOCK',     1),
                                            ('LOCK',        1),
                                            ]),
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
                                            ('',            3),
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
            Reg32 ('SEC1R',         0x070),
            ]

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq,
                 otp_base, otp_len, **kwargs):
        super().__init__(target, FLASH_2.REGS, 2048, ap, name, dev_base,
                         mem_base, max_write_freq, otp_base, otp_len, **kwargs)
        self.nbanks = 1
