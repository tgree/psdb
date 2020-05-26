# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class PWR(Device):
    '''
    Driver for the STM Power Control (PWR) device.
    '''
    REGS = [Reg32('CR1',       0x000),
            Reg32('CR2',       0x004),
            Reg32('CR3',       0x008),
            Reg32('CR4',       0x00C),
            Reg32('SR1',       0x010),
            Reg32('SR2',       0x014),
            Reg32('SCR',       0x018),
            Reg32('PUCRA',     0x020),
            Reg32('PDCRA',     0x024),
            Reg32('PUCRB',     0x028),
            Reg32('PDCRB',     0x02C),
            Reg32('PUCRC',     0x030),
            Reg32('PDCRC',     0x034),
            Reg32('PUCRD',     0x038),
            Reg32('PDCRD',     0x03C),
            Reg32('PUCRE',     0x040),
            Reg32('PDCRE',     0x044),
            Reg32('PUCRF',     0x048),
            Reg32('PDCRF',     0x04C),
            Reg32('PUCRG',     0x050),
            Reg32('PDCRG',     0x054),
            Reg32('CR5',       0x080),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(PWR, self).__init__(target, ap, addr, name, PWR.REGS, **kwargs)
