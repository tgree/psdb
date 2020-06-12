# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class DMA(Device):
    '''
    Driver for the STM32G4 DMAMUX device.
    '''
    REGS = [Reg32('ISR',    0x000),
            Reg32('IFCR',   0x004),
            Reg32('CCR1',   0x008),
            Reg32('CNDTR1', 0x00C),
            Reg32('CPAR1',  0x010),
            Reg32('CMAR1',  0x014),
            Reg32('CCR2',   0x01C),
            Reg32('CNDTR2', 0x020),
            Reg32('CPAR2',  0x024),
            Reg32('CMAR2',  0x028),
            Reg32('CCR3',   0x030),
            Reg32('CNDTR3', 0x034),
            Reg32('CPAR3',  0x038),
            Reg32('CMAR3',  0x03C),
            Reg32('CCR4',   0x044),
            Reg32('CNDTR4', 0x048),
            Reg32('CPAR4',  0x04C),
            Reg32('CMAR4',  0x050),
            Reg32('CCR5',   0x058),
            Reg32('CNDTR5', 0x05C),
            Reg32('CPAR5',  0x060),
            Reg32('CMAR5',  0x064),
            Reg32('CCR6',   0x06C),
            Reg32('CNDTR6', 0x070),
            Reg32('CPAR6',  0x074),
            Reg32('CMAR6',  0x078),
            Reg32('CCR7',   0x080),
            Reg32('CNDTR7', 0x084),
            Reg32('CPAR7',  0x088),
            Reg32('CMAR7',  0x08C),
            Reg32('CCR8',   0x094),
            Reg32('CNDTR8', 0x098),
            Reg32('CPAR8',  0x09C),
            Reg32('CMAR8',  0x0A0),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(DMA, self).__init__(target, ap, addr, name, DMA.REGS, **kwargs)
