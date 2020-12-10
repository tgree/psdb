# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class ART(Device):
    '''
    Driver for the STM32H7 Adaptive Realtime (ART) device.
    '''
    REGS = [Reg32('CTR',    0x00,  [('EN',          1),
                                    ('',            7),
                                    ('PCACHEADDR',  12),
                                    ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, ART.REGS, **kwargs)
