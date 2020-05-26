# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class BT(Device):
    '''
    Driver for the STM32G4 Basic Timer device (BT).

    According to the manual, these are mainly intended for use with the DAC.
    '''
    REGS = [Reg32('CR1',  0x00),
            Reg32('CR2',  0x04),
            Reg32('DIER', 0x0C),
            Reg32('SR',   0x10),
            Reg32('EGR',  0x14),
            Reg32('CNT',  0x24),
            Reg32('PSC',  0x28),
            Reg32('ARR',  0x2C),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(BT, self).__init__(target, ap, addr, name, BT.REGS, **kwargs)
