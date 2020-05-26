# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .flash import FLASH
from ..device import RegDiv, Reg32, Reg32R


class FLASH_DP(FLASH):
    '''
    Driver for the FLASH device on the STM32H7xx series of dual-core MCUs.
    '''
    OPT_REGS = [RegDiv('---Options'),
                Reg32 ('OPTSR_CUR',     0x01C),
                Reg32 ('OPTSR_PRG',     0x020),
                Reg32R('PRAR_CUR1',     0x028),
                Reg32 ('PRAR_PRG1',     0x02C),
                Reg32R('SCAR_CUR1',     0x030),
                Reg32 ('SCAR_PRG1',     0x034),
                Reg32R('WPSN_CUR1R',    0x038),
                Reg32 ('WPSN_PRG1R',    0x03C),
                Reg32R('BOOT7_CURR',    0x040),
                Reg32 ('BOOT7_PRGR',    0x044),
                Reg32R('BOOT4_CURR',    0x048),
                Reg32 ('BOOT4_PRGR',    0x04C),
                Reg32R('PRAR_CUR2',     0x128),
                Reg32 ('PRAR_PRG2',     0x12C),
                Reg32R('SCAR_CUR2',     0x130),
                Reg32 ('SCAR_PRG2',     0x134),
                Reg32R('WPSN_CUR2R',    0x138),
                Reg32 ('WPSN_PRG2R',    0x13C),
                ]

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq,
                 **kwargs):
        super(FLASH_DP, self).__init__(target, ap, name, dev_base, mem_base,
                                       max_write_freq, FLASH_DP.OPT_REGS,
                                       **kwargs)
