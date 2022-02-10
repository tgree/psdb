# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
from psdb.devices import AReg32
from .cortex_subdevice import CortexSubDevice


REGS = [AReg32('ITCTRL',            0xF00, [('IME',                 1),
                                            ]),
        AReg32('CLAIMSET',          0xFA0),
        AReg32('CLAIMCLR',          0xFA4),
        AReg32('DEVAFF0',           0xFA8),
        AReg32('DEVAFF1',           0xFAC),
        AReg32('LAR',               0xFB0, [('KEY',                 0,  31),
                                            ]),
        AReg32('LSR',               0xFB4, [('SLI',                 0),
                                            ('SLK',                 1),
                                            ('nTT',                 2),
                                            ]),
        AReg32('AUTHSTATUS',        0xFB8, [('NSID',                0,  1),
                                            ('NSNID',               2,  3),
                                            ('SID',                 4,  5),
                                            ('SNID',                6,  7),
                                            ]),
        AReg32('DEVARCH',           0xFBC, [('ARCHID',              0,  15),
                                            ('REVISION',            16, 19),
                                            ('PRESENT',             20),
                                            ('ARCHITECT',           21, 31),
                                            ]),
        AReg32('DEVID2',            0xFC0),
        AReg32('DEVID1',            0xFC4),
        AReg32('DEVID',             0xFC8),
        AReg32('DEVTYPE',           0xFCC, [('MAJOR',               0,  3),
                                            ('SUB',                 4,  7),
                                            ]),
        ]


def insert_reg_sorted(regs, r):
    for i, pr in enumerate(regs):
        if pr.offset > r.offset:
            regs.insert(i, r)
            return
    regs.append(r)


class CoreSight9Device(CortexSubDevice):
    def __init__(self, name, regs, component, subtype):
        assert ((component.cidr >> 12) & 0xF) == 9

        regs    = regs[:]
        offsets = set(r.offset for r in regs)
        for c9r in REGS:
            if c9r.offset not in offsets:
                insert_reg_sorted(regs, c9r)

        super().__init__(name, regs, component, subtype)
