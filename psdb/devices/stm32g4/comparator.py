# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class COMP(Device):
    '''
    Driver for the STM32G4 analog comparator device (COMP).
    '''
    REGS = [Reg32('CSR1', 0x00),
            Reg32('CSR2', 0x04),
            Reg32('CSR3', 0x08),
            Reg32('CSR4', 0x0C),
            Reg32('CSR5', 0x10),
            Reg32('CSR6', 0x14),
            Reg32('CSR7', 0x18),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(COMP, self).__init__(target, ap, addr, name, COMP.REGS, **kwargs)
