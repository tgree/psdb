# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32


class DAC(Device):
    '''
    Driver for the STM32 DAC.
    '''
    REGS = [AReg32('CR',      0x000,   [('EN1',              0),
                                        ('TEN1',             1),
                                        ('TSEL',             2,  5),
                                        ('WAVE1',            6,  7),
                                        ('MAMP1',            8, 11),
                                        ('DMAEN1',          12),
                                        ('DMAUDRIE1',       13),
                                        ('CEN1',            14),
                                        ('EN2',             16),
                                        ('TEN2',            17),
                                        ('TSESL2',          18, 21),
                                        ('WAVE2',           22, 23),
                                        ('MAMP2',           24, 27),
                                        ('DMAEN2',          28),
                                        ('DMAUDRIE2',       29),
                                        ('CEN2',            30),
                                        ]),
            AReg32('SWTRGR',  0x004,   [('SWTRIG1',          0),
                                        ('SWTRIG2',          1),
                                        ]),
            AReg32('DHR12R1', 0x008,   [('DACC1DHR',         0, 11)]),
            AReg32('DHR12L1', 0x00C,   [('DACC1DHR',         4, 15)]),
            AReg32('DHR8R1',  0x010,   [('DACC1DHR',         0,  7)]),
            AReg32('DHR12R2', 0x014,   [('DACC2DHR',         0, 11)]),
            AReg32('DHR12L2', 0x018,   [('DACC2DHR',         4, 15)]),
            AReg32('DHR8R2',  0x01C,   [('DACC2DHR',         0,  7)]),
            AReg32('DHR12RD', 0x020,   [('DACC1DHR',         0, 11),
                                        ('DACC2DHR',        16, 27),
                                        ]),
            AReg32('DHR12LD', 0x024,   [('DACC1DHR',         4, 15),
                                        ('DACC2DHR',        20, 31),
                                        ]),
            AReg32('DHR8RD',  0x028,   [('DACC1DHR',         0,  7),
                                        ('DACC2DHR',         8, 15),
                                        ]),
            AReg32('DOR1',    0x02C,   [('DACC1DOR',         0, 11)]),
            AReg32('DOR2',    0x030,   [('DACC2DOR',         0, 11)]),
            AReg32('SR',      0x034,   [('DMAUDR1',         13),
                                        ('CAL_FLAG1',       14),
                                        ('BWST1',           15),
                                        ('DMAUDR2',         29),
                                        ('CAL_FLAG2',       30),
                                        ('BWST2',           31),
                                        ]),
            AReg32('CCR',     0x038,   [('OTRIM1',           0,  4),
                                        ('OTRIM2',          16, 20),
                                        ]),
            AReg32('MCR',     0x03C,   [('MODE1',            0,  3),
                                        ('MODE2',           16, 18),
                                        ]),
            AReg32('SHSR1',   0x040,   [('TSAMPLE1',         0,  9)]),
            AReg32('SHSR2',   0x044,   [('TSAMPLE2',         0,  9)]),
            AReg32('SHHR',    0x048,   [('THOLD1',           0,  9),
                                        ('THOLD2',          16, 25),
                                        ]),
            AReg32('SHRR',    0x04C,   [('TREFRESH1',        0,  7),
                                        ('TREFRESH2',       16, 23),
                                        ]),
            ]

    def __init__(self, target, ap, name, addr, sub_regs=None, **kwargs):
        regs = DAC.REGS + (sub_regs or [])
        super(DAC, self).__init__(target, ap, addr, name, regs, **kwargs)


class DAC_Saw(DAC):
    '''
    Driver for DACs that have sawtooth functionality (STM32G4).

    The STM32G4 DAC can also take two values at once for a single channel,
    halving the number of DMA accesses required to generate a signal.
    '''
    STREGS = [AReg32('STR1',   0x058),
              AReg32('STR2',   0x05C),
              AReg32('STMODR', 0x060),
              ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(DAC_Saw, self).__init__(target, ap, name, addr,
                                      sub_regs=DAC_Saw.STREGS, **kwargs)
