# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32, Reg32W


class TIM17(Device):
    '''
    Driver for the H7 TIM17 General-purpose Timer device (GPT).
    '''
    REGS = [Reg32 ('CR1',       0x000,     [('CEN',         1),
                                            ('UDIS',        1),
                                            ('URS',         1),
                                            ('OPM',         1),
                                            ('',            3),
                                            ('ARPE',        1),
                                            ('CKD',         2),     # tDTS
                                            ('',            1),
                                            ('UIFREMAP',    1),
                                            ]),
            Reg32 ('CR2',       0x004,     [('CCPC',        1),
                                            ('',            1),
                                            ('CCUS',        1),
                                            ('CCDS',        1),
                                            ('',            4),
                                            ('OIS1',        1),
                                            ('OIS1N',       1),
                                            ]),
            Reg32 ('DIER',      0x00C,     [('UIE',         1),
                                            ('CC1IE',       1),
                                            ('',            3),
                                            ('COMIE',       1),
                                            ('',            1),
                                            ('BIE',         1),
                                            ('UDE',         1),
                                            ('CC1DE',       1),
                                            ]),
            Reg32 ('SR',        0x010,     [('UIF',         1),
                                            ('CC1IF',       1),
                                            ('',            3),
                                            ('COMIF',       1),
                                            ('',            1),
                                            ('BIF',         1),
                                            ('',            1),
                                            ('CC1OF',       1),
                                            ]),
            Reg32W('EGR',       0x014,     [('UG',          1),
                                            ('CC1G',        1),
                                            ('',            3),
                                            ('COMG',        1),
                                            ('',            1),
                                            ('BG',          1),
                                            ]),
            Reg32 ('CCMR1_I',   0x018,     [('CC1S',        2),
                                            ('IC1PSC',      2),
                                            ('IC1F',        4),
                                            ]),
            Reg32 ('CCMR1_O',   0x018,     [('CC1S',        2),
                                            ('OC1FE',       1),
                                            ('OC1PE',       1),
                                            ('OC1M[2:0]',   3),
                                            ('',            9),
                                            ('OC1M[3]',     1),
                                            ]),
            Reg32 ('CCER',      0x020,     [('CC1E',        1),
                                            ('CC1P',        1),
                                            ('CC1NE',       1),
                                            ('CC1NP',       1),
                                            ]),
            Reg32 ('CNT',       0x024,     [('CNT',         16),
                                            ('',            15),
                                            ('UIFCPY',      1),
                                            ]),
            Reg32 ('PSC',       0x028,     [('PSC',         16),
                                            ]),
            Reg32 ('ARR',       0x02C,     [('ARR',         16),
                                            ]),
            Reg32 ('RCR',       0x030,     [('REP',         8),
                                            ]),
            Reg32 ('CCR1',      0x034,     [('CCR1',        16),
                                            ]),
            Reg32 ('BDTR',      0x044,     [('DTG',         8),
                                            ('LOCK',        2),
                                            ('OSSI',        1),
                                            ('OSSR',        1),
                                            ('BKE',         1),
                                            ('BKP',         1),
                                            ('AOE',         1),
                                            ('MOE',         1),
                                            ('BKF',         4),
                                            ]),
            Reg32 ('DCR',       0x048,     [('DBA',         5),
                                            ('',            3),
                                            ('DBL',         5),
                                            ]),
            Reg32 ('DMAR',      0x04C,     [('DMAB',        16),
                                            ]),
            Reg32 ('AF1',       0x060,     [('BKINE',       1),
                                            ('BKCMP1E',     1),
                                            ('BKCMP2E',     1),
                                            ('',            5),
                                            ('BKDF1BK1E',   1),
                                            ('BKINP',       1),
                                            ('BKCMP1P',     1),
                                            ('BKCMP2P',     1),
                                            ]),
            Reg32 ('TISEL',     0x068,     [('TI1SEL',      4),
                                            ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(TIM17, self).__init__(target, ap, addr, name, TIM17.REGS,
                                    **kwargs)