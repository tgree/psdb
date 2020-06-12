# Copyright (c) 2019-2020 Phase Advanced Sensor Systems, Inc.
from psdb.devices import Reg32, Reg32R, Reg32W
from . import scs_base

import collections


# The core registers and the selector value they map to in the DCRSR.
CORE_REGISTERS = collections.OrderedDict([
    ('r0',      0),
    ('r1',      1),
    ('r2',      2),
    ('r3',      3),
    ('r4',      4),
    ('r5',      5),
    ('r6',      6),
    ('r7',      7),
    ('r8',      8),
    ('r9',      9),
    ('r10',     10),
    ('r11',     11),
    ('r12',     12),
    ('sp',      13),
    ('lr',      14),
    ('pc',      15),
    ('xpsr',    16),
    ('msp',     17),
    ('psp',     18),
    ('cp',      20),   # CONTROL, PRIMASK
])


class SCS(scs_base.SCS):
    '''
    Driver for Cortex V6-M (M0+) System Control Space.

    The SCS has registers that can be used to enable the DWT and ITM units; we
    need to enable them before allowing component probing to advance otherwise
    we will attempt to probe components that aren't enabled yet.
    '''
    REGS = [Reg32 ('ACTLR',  0x008),
            Reg32R('CPUID',  0xD00, [('REVISION',    4),
                                     ('PARTNO',     12),
                                     ('_1100',       4),
                                     ('VARIANT',     4),
                                     ('IMPLEMENTER', 8),
                                     ]),
            Reg32 ('ICSR',   0xD04, [('VECTACTIVE',  9),
                                     ('',            3),
                                     ('VECTPENDING', 9),
                                     ('',            1),
                                     ('ISRPENDING',  1),
                                     ('ISRPREEMPT',  1),
                                     ('',            1),
                                     ('PENDSTCLR',   1),
                                     ('PENDSTSET',   1),
                                     ('PENDSVCLR',   1),
                                     ('PENDSVSET',   1),
                                     ('',            2),
                                     ('NMIPENDSET',  1),
                                     ]),
            Reg32 ('VTOR',   0xD08, [('',        7),
                                     ('TBLOFF', 25),
                                     ]),
            Reg32 ('AIRCR',  0xD0C, [('',              0),
                                     ('VECTCLRACTIVE', 1),
                                     ('SYSRESETREQ',   1),
                                     ('',             12),
                                     ('ENDIANNESS',    1),
                                     ('VECTKEYSTAT',  16),
                                     ]),
            Reg32 ('SCR',    0xD10, [('',              1),
                                     ('SLEEPONEXIT',   1),
                                     ('SLEEPDEEP',     1),
                                     ('',              1),
                                     ('SEVONPEND',     1),
                                     ]),
            Reg32 ('CCR',    0xD14, [('',               3),
                                     ('UNALIGN_TRP',    1),
                                     ('',               5),
                                     ('STKALIGN',       1),
                                     ('',               6),
                                     ]),
            Reg32 ('SHPR2',  0xD1C, [('',           30),
                                     ('PRI_11',     2),
                                     ]),
            Reg32 ('SHPR3',  0xD20, [('',           22),
                                     ('PRI_14',     2),
                                     ('',           6),
                                     ('PRI_15',     2),
                                     ]),
            Reg32 ('SHCSR',  0xD24, [('',               15),
                                     ('SVCALLPENDED',   1),
                                     ]),
            Reg32 ('DFSR',   0xD30, [('HALTED',      1),
                                     ('BKPT',        1),
                                     ('DWTTRAP',     1),
                                     ('VCATCH',      1),
                                     ('EXTERNAL',    1),
                                     ]),
            Reg32 ('DHCSR',  0xDF0, [('C_DEBUGEN',     1),
                                     ('C_HALT',        1),
                                     ('C_STEP',        1),
                                     ('C_MASKINTS',    1),
                                     ('',             12),
                                     ('S_REGRDY',      1),
                                     ('S_HALT',        1),
                                     ('S_SLEEP',       1),
                                     ('S_LOCKUP',      1),
                                     ('',              4),
                                     ('S_RETIRE_ST',   1),
                                     ('S_RESET_ST',    1),
                                     ]),
            Reg32W('DCRSR',  0xDF4, [('REGSEL',    5),
                                     ('',          11),
                                     ('REGWnR',    1),
                                     ]),
            Reg32 ('DCRDR',  0xDF8),
            Reg32 ('DEMCR',  0xDFC, [('VC_CORERESET', 1),
                                     ('',             9),
                                     ('VC_HARDERR',   1),
                                     ('',             13),
                                     ('DWTENA',       1),
                                     ]),
            ]

    def __init__(self, component, subtype):
        super(SCS, self).__init__(component, subtype, SCS.REGS, CORE_REGISTERS)

        # Enable DEMCR.DWTENA so we can probe further.
        self._DEMCR.DWTENA = 1
