# Copyright (c) 2023 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32, AReg32S


class CORDIC(Device):
    '''
    Driver for the STM32G4/U5 CORDIC unit.
    '''
    REGS = [AReg32('CSR',       0x00,  [('FUNC',        0,  3),
                                        ('PRECISION',   4,  7),
                                        ('SCALE',       8,  10),
                                        ('IEN',         16),
                                        ('DMAREN',      17),
                                        ('DMAWEN',      18),
                                        ('NRES',        19),
                                        ('NARGS',       20),
                                        ('RESSIZE',     21),
                                        ('ARGSIZE',     22),
                                        ('RRDY',        31),
                                        ]),
            AReg32('WDATA',     0x04,  [('ARG',         0,  31),
                                        ]),
            AReg32S('RDATA',    0x08,  [('RES',         0,  31),
                                        ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, CORDIC.REGS, **kwargs)
