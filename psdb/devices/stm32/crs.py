# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32


class CRS(Device):
    '''
    Driver for the STM32 Clock Recovery System (CRS) device.
    '''
    REGS = [AReg32('CR',    0x000, [('SYNCOKIE',        0),
                                    ('SYNCWARNIE',      1),
                                    ('ERRIE',           2),
                                    ('ESYNCIE',         3),
                                    ('CEN',             5),
                                    ('AUTOTRIMEN',      6),
                                    ('SWSYNC',          7),
                                    ('TRIM',            8,  14),
                                    ]),
            AReg32('CFGR',  0x004, [('RELOAD',          0,  15),
                                    ('FELIM',           16, 23),
                                    ('SYNCDIV',         24, 26),
                                    ('SYNCSRC',         28, 29),
                                    ('SYNCPOL',         31),
                                    ]),
            AReg32('ISR',   0x008, [('SYNCOKF',         0),
                                    ('SYNCWARNF',       1),
                                    ('ERRF',            2),
                                    ('ESYNCF',          3),
                                    ('SYNCERR',         8),
                                    ('SYNCMISS',        9),
                                    ('TRIMOVF',         10),
                                    ('FEDIR',           15),
                                    ('FECAP',           16,  31),
                                    ]),
            AReg32('ICR',   0x00C, [('SYNCOKC',         0),
                                    ('SYNCWARNC',       1),
                                    ('ERRC',            2),
                                    ('ESYNCC',          3),
                                    ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, CRS.REGS, **kwargs)
