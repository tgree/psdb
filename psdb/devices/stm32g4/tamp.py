# Copyright (c) 2021 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32


class TAMP(Device):
    '''
    Driver for the STM32G4 tamper-detection device (TAMP).
    '''
    REGS = [AReg32('CR1',       0x00,  [('TAMP1E',      0),
                                        ('TAMP2E',      1),
                                        ('TAMP3E',      2),
                                        ('ITAMP3E',     18),
                                        ('ITAMP4E',     19),
                                        ('ITAMP5E',     20),
                                        ('ITAMP6E',     21),
                                        ]),
            AReg32('CR2',       0x04,  [('TAMP1NOER',   0),
                                        ('TAMP2NOER',   1),
                                        ('TAMP3NOER',   2),
                                        ('TAMP1MSK',    16),
                                        ('TAMP2MSK',    17),
                                        ('TAMP3MSK',    18),
                                        ('TAMP1TRG',    24),
                                        ('TAMP2TRG',    25),
                                        ('TAMP3TRG',    26),
                                        ]),
            AReg32('FLTCR',     0x0C,  [('TAMPFREQ',    0, 2),
                                        ('TAMPFLT',     3, 4),
                                        ('TAMPPRCH',    5, 6),
                                        ('TAMPPUDIS',   7),
                                        ]),
            AReg32('IER',       0x2C,  [('TAMP1IE',     0),
                                        ('TAMP2IE',     1),
                                        ('TAMP3IE',     2),
                                        ('ITAMP3IE',    18),
                                        ('ITAMP4IE',    19),
                                        ('ITAMP5IE',    20),
                                        ('ITAMP6IE',    21),
                                        ]),
            AReg32('SR',        0x30,  [('TAMP1F',      0),
                                        ('TAMP2F',      1),
                                        ('TAMP3F',      2),
                                        ('ITAMP3F',     18),
                                        ('ITAMP4F',     19),
                                        ('ITAMP5F',     20),
                                        ('ITAMP6F',     21),
                                        ]),
            AReg32('MISR',      0x34,  [('TAMP1MF',     0),
                                        ('TAMP2MF',     1),
                                        ('TAMP3MF',     2),
                                        ('ITAMP3MF',    18),
                                        ('ITAMP4MF',    19),
                                        ('ITAMP5MF',    20),
                                        ('ITAMP6MF',    21),
                                        ]),
            AReg32('SCR',       0x3C,  [('CTAMP1F',     0),
                                        ('CTAMP2F',     1),
                                        ('CTAMP3F',     2),
                                        ('CITAMP3F',    18),
                                        ('CITAMP4F',    19),
                                        ('CITAMP5F',    20),
                                        ('CITAMP6F',    21),
                                        ]),
            AReg32('BKP0R',     0x100 +  0*4),
            AReg32('BKP1R',     0x100 +  1*4),
            AReg32('BKP2R',     0x100 +  2*4),
            AReg32('BKP3R',     0x100 +  3*4),
            AReg32('BKP4R',     0x100 +  4*4),
            AReg32('BKP5R',     0x100 +  5*4),
            AReg32('BKP6R',     0x100 +  6*4),
            AReg32('BKP7R',     0x100 +  7*4),
            AReg32('BKP8R',     0x100 +  8*4),
            AReg32('BKP9R',     0x100 +  9*4),
            AReg32('BKP10R',    0x100 + 10*4),
            AReg32('BKP11R',    0x100 + 11*4),
            AReg32('BKP12R',    0x100 + 12*4),
            AReg32('BKP13R',    0x100 + 13*4),
            AReg32('BKP14R',    0x100 + 14*4),
            AReg32('BKP15R',    0x100 + 15*4),
            AReg32('BKP16R',    0x100 + 16*4),
            AReg32('BKP17R',    0x100 + 17*4),
            AReg32('BKP18R',    0x100 + 18*4),
            AReg32('BKP19R',    0x100 + 19*4),
            AReg32('BKP20R',    0x100 + 20*4),
            AReg32('BKP21R',    0x100 + 21*4),
            AReg32('BKP22R',    0x100 + 22*4),
            AReg32('BKP23R',    0x100 + 23*4),
            AReg32('BKP24R',    0x100 + 24*4),
            AReg32('BKP25R',    0x100 + 25*4),
            AReg32('BKP26R',    0x100 + 26*4),
            AReg32('BKP27R',    0x100 + 27*4),
            AReg32('BKP28R',    0x100 + 28*4),
            AReg32('BKP29R',    0x100 + 29*4),
            AReg32('BKP30R',    0x100 + 30*4),
            AReg32('BKP31R',    0x100 + 31*4),
            ]
    
    def __init__(self, target, ap, name, addr, **kwargs):
        super(TAMP, self).__init__(target, ap, addr, name, TAMP.REGS, **kwargs)