# Copyright (c) 2024 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32, Reg32W


class TIM3(Device):
    '''
    Driver for the TIM3 peripheral on STM32C0.
    '''
    REGS = [Reg32 ('CR1',    0x000),
            Reg32 ('CR2',    0x004),
            Reg32 ('SMCR',   0x008),
            Reg32 ('DIER',   0x00C),
            Reg32 ('SR',     0x010),
            Reg32W('EGR',    0x014),
            Reg32 ('CCMR1',  0x018),
            Reg32 ('CCMR2',  0x01C),
            Reg32 ('CCER',   0x020),
            Reg32 ('CNT',    0x024),
            Reg32 ('PSC',    0x028),
            Reg32 ('ARR',    0x02C),
            Reg32 ('CCR1',   0x034),
            Reg32 ('CCR2',   0x038),
            Reg32 ('CCR3',   0x03C),
            Reg32 ('CCR4',   0x040),
            Reg32 ('DCR',    0x048),
            Reg32 ('DMAR',   0x04C),
            Reg32 ('AF1',    0x060),
            Reg32 ('TISEL',  0x068),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, TIM3.REGS, **kwargs)
