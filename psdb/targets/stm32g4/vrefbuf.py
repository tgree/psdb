# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class VREF(Device):
    '''
    Driver for the STM32G4 VREF Buffer.
    '''
    REGS = [Reg32 ('CSR', 0x00),
            Reg32 ('CCR', 0x04),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(VREF, self).__init__(target, ap, addr, name, VREF.REGS, **kwargs)
