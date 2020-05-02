# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Reg32, Reg32W
from .flash_base import FLASH_Base


class FLASH_4(FLASH_Base):
    '''
    Driver for the FLASH category 4 device on the STM32G4 series of MCUs:
        STM32G491
        STM32G4A1
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
                                            ('',            2),
                                            ('PB4_PUPEN',   1),
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
                 otp_base, otp_len):
        FLASH_Base.__init__(self, FLASH_4.REGS, 2048, target, ap, name,
                            dev_base, mem_base, max_write_freq, otp_base,
                            otp_len)
