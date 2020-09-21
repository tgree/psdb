# Copyright (c) 2019-2020 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class VREF(Device):
    '''
    Driver for the STM32 VREF Buffer.
    '''
    REGS = [Reg32('CSR',    0x00,  [('ENVR',    1),
                                    ('HIZ',     1),
                                    ('',        1),
                                    ('VRR',     1),
                                    ('VRS',     3),
                                    ]),
            Reg32('CCR',    0x04,  [('TRIM',    6),
                                    ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(VREF, self).__init__(target, ap, addr, name, VREF.REGS, **kwargs)
