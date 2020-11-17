# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class TIM6(Device):
    '''
    Driver for the STM32H7 Basic Timer device (BT).

    According to the manual, these are mainly intended for use with the DAC.
    '''
    REGS = [Reg32('CR1',    0x00,  [('CEN',         1),
                                    ('UDIS',        1),
                                    ('URS',         1),
                                    ('OPM',         1),
                                    ('',            3),
                                    ('ARPE',        1),
                                    ('',            3),
                                    ('UIFREMAP',    1),
                                    ]),
            Reg32('CR2',    0x04,  [('',            4),
                                    ('MMS',         3),
                                    ]),
            Reg32('DIER',   0x0C,  [('UIE',         1),
                                    ('',            7),
                                    ('UDE',         1),
                                    ]),
            Reg32('SR',     0x10,  [('UIF',         1),
                                    ]),
            Reg32('EGR',    0x14,  [('UG',          1),
                                    ]),
            Reg32('CNT',    0x24,  [('CNT',         16),
                                    ('',            15),
                                    ('UIFCPY',      1),
                                    ]),
            Reg32('PSC',    0x28,  [('PSC',         16),
                                    ]),
            Reg32('ARR',    0x2C,  [('ARR',         15),
                                    ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(TIM6, self).__init__(target, ap, addr, name, TIM6.REGS, **kwargs)
