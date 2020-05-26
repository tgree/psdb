# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class OPAMP(Device):
    '''
    Driver for the STM32G4 opamp device (OPAMP).
    '''
    REGS = [Reg32('CSR1',  0x00),
            Reg32('CSR2',  0x04),
            Reg32('CSR3',  0x08),
            Reg32('CSR4',  0x0C),
            Reg32('CSR5',  0x10),
            Reg32('CSR6',  0x14),
            Reg32('TCMR1', 0x18),
            Reg32('TCMR2', 0x1C),
            Reg32('TCMR3', 0x20),
            Reg32('TCMR4', 0x24),
            Reg32('TCMR5', 0x28),
            Reg32('TCMR6', 0x2C),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(OPAMP, self).__init__(target, ap, addr, name, OPAMP.REGS,
                                    **kwargs)
