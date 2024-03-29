# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32


class TIM2_5(Device):
    '''
    Driver for the STM32H7 TIM2 and TIM5 devices.
    '''
    REGS = [AReg32('CR1',       0x000,    [('CEN',                 0),
                                           ('UDIS',                1),
                                           ('URS',                 2),
                                           ('OPM',                 3),
                                           ('DIR',                 4),
                                           ('CMS',                 5,  6),
                                           ('ARPE',                7),
                                           ('CKD',                 8,  9),
                                           ('UIFREMAP',            11),
                                           ]),
            AReg32('CR2',       0x004,    [('CCDS',                3),
                                           ('MMS',                 4,  6),
                                           ('TI1S',                7),
                                           ]),
            AReg32('SMCR',      0x008,    [('SMS2_0',              0,  2),
                                           ('TS2_0',               4,  6),
                                           ('MSM',                 7),
                                           ('ETF',                 8,  11),
                                           ('ETPS',                12, 13),
                                           ('ECE',                 14),
                                           ('ETP',                 15),
                                           ('SMS_3',               16),
                                           ('TS4_3',               20, 21),
                                           ]),
            AReg32('DIER',      0x00C,    [('UIE',                 0),
                                           ('CC1IE',               1),
                                           ('CC2IE',               2),
                                           ('CC3IE',               3),
                                           ('CC4IE',               4),
                                           ('TIE',                 6),
                                           ('UDE',                 8),
                                           ('CC1DE',               9),
                                           ('CC2DE',               10),
                                           ('CC3DE',               11),
                                           ('CC4DE',               12),
                                           ('TDE',                 14),
                                           ]),
            AReg32('SR',        0x010,    [('UIF',                 0),
                                           ('CC1IF',               1),
                                           ('CC2IF',               2),
                                           ('CC3IF',               3),
                                           ('CC4IF',               4),
                                           ('TIF',                 6),
                                           ('CC1OF',               9),
                                           ('CC2OF',               10),
                                           ('CC3OF',               11),
                                           ('CC4OF',               12),
                                           ]),
            AReg32('EGR',       0x014,    [('UG',                  0),
                                           ('CC1G',                1),
                                           ('CC2G',                2),
                                           ('CC3G',                3),
                                           ('CC4G',                4),
                                           ('TG',                  6),
                                           ]),
            AReg32('CCMR1_I',   0x018,    [('CC1S',                0,  1),
                                           ('IC1PSC',              2,  3),
                                           ('IC1F',                4,  7),
                                           ('CC2S',                8,  9),
                                           ('IC2PSC',              10, 11),
                                           ('IC2F',                12, 15),
                                           ]),
            AReg32('CCMR1_O',   0x018,    [('CC1S',                0,  1),
                                           ('OC1FE',               2),
                                           ('OC1PE',               3),
                                           ('OC1M2_0',             4,  6),
                                           ('OC1CE',               7),
                                           ('CC2S',                8,  9),
                                           ('OC2FE',               10),
                                           ('OC2PE',               11),
                                           ('OC2M2_0',             12, 14),
                                           ('OC2CE',               15),
                                           ('OC1M_3',              16),
                                           ('OC2M_3',              24),
                                           ]),
            AReg32('CCMR2_I',   0x01C,    [('CC3S',                0,  1),
                                           ('IC3PSC',              2,  3),
                                           ('IC3F',                4,  7),
                                           ('CC4S',                8,  9),
                                           ('IC4PSC',              10, 11),
                                           ('IC4F',                12, 15),
                                           ]),
            AReg32('CCMR2_O',   0x01C,    [('CC3S',                0,  1),
                                           ('OC3FE',               2),
                                           ('OC3PE',               3),
                                           ('OC3M2_0',             4,  6),
                                           ('OC3CE',               7),
                                           ('CC4S',                8,  9),
                                           ('OC4FE',               10),
                                           ('OC4PE',               11),
                                           ('OC4M2_0',             12, 14),
                                           ('OC4CE',               15),
                                           ('OC3M_3',              16),
                                           ('OC4M_3',              24),
                                           ]),
            AReg32('CCER',      0x020,    [('CC1E',                0),
                                           ('CC1P',                1),
                                           ('CC1NP',               3),
                                           ('CC2E',                4),
                                           ('CC2P',                5),
                                           ('CC2NP',               7),
                                           ('CC3E',                8),
                                           ('CC3P',                9),
                                           ('CC3NP',               11),
                                           ('CC4E',                12),
                                           ('CC4P',                13),
                                           ('CC4NP',               15),
                                           ]),
            AReg32('CNT',       0x024),
            AReg32('PSC',       0x028),
            AReg32('ARR',       0x02C),
            AReg32('CCR1',      0x034),
            AReg32('CCR2',      0x038),
            AReg32('CCR3',      0x03C),
            AReg32('CCR4',      0x040),
            AReg32('DCR',       0x048,    [('DBA',                 0,  4),
                                           ('DBL',                 8,  12),
                                           ]),
            AReg32('DMAR',      0x04C,    [('DMAB',                0,  15),
                                           ]),
            AReg32('AF1',       0x060,    [('ETRSEL',              14, 17),
                                           ]),
            AReg32('TISEL',     0x068,    [('TI1SEL',              0,  3),
                                           ('TI2SEL',              8,  11),
                                           ('TI3SEL',              16, 19),
                                           ('TI4SEL',              24, 27),
                                           ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, TIM2_5.REGS, **kwargs)
