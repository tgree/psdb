# Copyright (c) 2019-2021 Phase Advanced Sensor Systems, Inc.
import collections

from psdb.devices import AReg32, AReg32R, AReg32W
from . import scs_base


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
    ('cfbp',    20),   # CONTROL, FAULTMASK, BASEPRI, PRIMASK
    ('fpscr',   33),
    ('s0',      64),
    ('s1',      65),
    ('s2',      66),
    ('s3',      67),
    ('s4',      68),
    ('s5',      69),
    ('s6',      70),
    ('s7',      71),
    ('s8',      72),
    ('s9',      73),
    ('s10',     74),
    ('s11',     75),
    ('s12',     76),
    ('s13',     77),
    ('s14',     78),
    ('s15',     79),
    ('s16',     80),
    ('s17',     81),
    ('s18',     82),
    ('s19',     83),
    ('s20',     84),
    ('s21',     85),
    ('s22',     86),
    ('s23',     87),
    ('s24',     88),
    ('s25',     89),
    ('s26',     90),
    ('s27',     91),
    ('s28',     92),
    ('s29',     93),
    ('s30',     94),
    ('s31',     95),
])


class SCS(scs_base.SCS):
    '''
    Driver for Cortex V8-M (M33) System Control Space.
    '''
    REGS = [AReg32R('ICTR',         0x004, [('INTLINESNUM',         0,  3),
                                            ]),
            AReg32('ACTLR',         0x008),
            AReg32('CPPWR',         0x00C, [('SU0',                 0),
                                            ('SUS0',                1),
                                            ('SU1',                 2),
                                            ('SUS1',                3),
                                            ('SU2',                 4),
                                            ('SUS2',                5),
                                            ('SU3',                 6),
                                            ('SUS3',                7),
                                            ('SU4',                 8),
                                            ('SUS4',                9),
                                            ('SU5',                 10),
                                            ('SUS5',                11),
                                            ('SU6',                 12),
                                            ('SUS6',                13),
                                            ('SU7',                 14),
                                            ('SUS7',                15),
                                            ('SU10',                20),
                                            ('SUS10',               21),
                                            ('SU11',                22),
                                            ('SUS11',               23),
                                            ]),
            AReg32('SYST_CSR',      0x010, [('ENABLE',              0),
                                            ('TICKINT',             1),
                                            ('CLKSOURCE',           2),
                                            ('COUNTFLAG',           16),
                                            ]),
            AReg32('SYST_RVR',      0x014, [('RELOAD',              0,  23),
                                            ]),
            AReg32('SYST_CVR',      0x018, [('CURRENT',             0,  23),
                                            ]),
            AReg32('SYST_CALIB',    0x01C, [('TENMS',               0,  23),
                                            ('SKEW',                30),
                                            ('NOREF',               31),
                                            ]),
            AReg32R('REVIDR',       0xCFC),
            AReg32R('CPUID',        0xD00, [('REVISION',            0,  3),
                                            ('PARTNO',              4,  15),
                                            ('ARCHITECTURE',        16, 19),
                                            ('VARIANT',             20, 23),
                                            ('IMPLEMENTER',         24, 31),
                                            ]),
            AReg32('ICSR',          0xD04, [('VECTACTIVE',          0,  8),
                                            ('RETTOBASE',           11),
                                            ('VECTPENDING',         12, 20),
                                            ('ISRPENDING',          22),
                                            ('ISRPREEMPT',          23),
                                            ('STTNS',               24),
                                            ('PENDSTCLR',           25),
                                            ('PENDSTSET',           26),
                                            ('PENDSVCLR',           27),
                                            ('PENDSVSET',           28),
                                            ('PENDNMICLR',          30),
                                            ('PENDNMISET',          31),
                                            ]),
            AReg32('VTOR',          0xD08, [('TBLOFF',              7,  31),
                                            ]),
            AReg32('AIRCR',         0xD0C, [('VECTCLRACTIVE',       1),
                                            ('SYSRESETREQ',         2),
                                            ('SYSRESETREQS',        3),
                                            ('DIT',                 4),
                                            ('IESB',                5),
                                            ('PRIGROUP',            8,  10),
                                            ('BFHFNMINS',           13),
                                            ('PRIS',                14),
                                            ('ENDIANNESS',          15),
                                            ('VECTKEYSTAT',         16, 31),
                                            ]),
            AReg32('SCR',           0xD10, [('SLEEPONEXIT',         1),
                                            ('SLEEPDEEP',           2),
                                            ('SLEEPDEEPS',          3),
                                            ('SEVONPEND',           4),
                                            ]),
            AReg32('CCR',           0xD14, [('USERSETMPEND',        1),
                                            ('UNALIGN_TRP',         3),
                                            ('DIV_0_TRP',           4),
                                            ('BFHFNMIGN',           8),
                                            ('STKOFHFNMIGN',        10),
                                            ('DC',                  16),
                                            ('IC',                  17),
                                            ('BP',                  18),
                                            ('LOB',                 19),
                                            ('TRD',                 20),
                                            ]),
            AReg32('SHPR1',         0xD18, [('PRI_4',               0,  7),
                                            ('PRI_5',               8,  15),
                                            ('PRI_6',               16, 23),
                                            ('PRI_7',               24, 31),
                                            ]),
            AReg32('SHPR2',         0xD1C, [('PRI_8',               0,  7),
                                            ('PRI_9',               8,  15),
                                            ('PRI_10',              16, 23),
                                            ('PRI_11',              24, 31),
                                            ]),
            AReg32('SHPR3',         0xD20, [('PRI_12',              0,  7),
                                            ('PRI_13',              8,  15),
                                            ('PRI_14',              16, 23),
                                            ('PRI_15',              24, 31),
                                            ]),
            AReg32('SHCSR',         0xD24, [('MEMFAULTACT',         0),
                                            ('BUSFAULTACT',         1),
                                            ('HARDFAULTACT',        2),
                                            ('USGFAULTACT',         3),
                                            ('SECUREFAULTACT',      4),
                                            ('NMIACT',              5),
                                            ('SVCALLACT',           7),
                                            ('MONITORACT',          8),
                                            ('PENDSVACT',           10),
                                            ('SYSTICKACT',          11),
                                            ('USGFAULTPENDED',      12),
                                            ('MEMFAULTPENDED',      13),
                                            ('BUSFAULTPENDED',      14),
                                            ('SVCALLPENDED',        15),
                                            ('MEMFAULTENA',         16),
                                            ('BUSFAULTENA',         17),
                                            ('USGFAULTENA',         18),
                                            ('SECUREFAULTENA',      19),
                                            ('SECUREFAULTPENDED',   20),
                                            ('HARDFAULTPENDED',     21),
                                            ]),
            AReg32('CFSR',          0xD28, [('IACCVIOL',            0),
                                            ('DACCVIOL',            1),
                                            ('MUNSTKERR',           3),
                                            ('MSTKERR',             4),
                                            ('MLSPERR',             5),
                                            ('MMARVALID',           7),
                                            ('IBUSERR',             8),
                                            ('PRECISERR',           9),
                                            ('IMPRECISERR',         10),
                                            ('UNSTKERR',            11),
                                            ('STKERR',              12),
                                            ('LSPERR',              13),
                                            ('BFARVALID',           15),
                                            ('UNDEFINSTR',          16),
                                            ('INVSTATE',            17),
                                            ('INVPC',               18),
                                            ('NOCP',                19),
                                            ('STKOF',               20),
                                            ('UNALIGNED',           24),
                                            ('DIVBYZERO',           25),
                                            ]),
            AReg32('HFSR',          0xD2C, [('VECTTBL',             1),
                                            ('FORCED',              30),
                                            ('DEBUGEVT',            31),
                                            ]),
            AReg32('DFSR',          0xD30, [('HALTED',              0),
                                            ('BKPT',                1),
                                            ('DWTTRAP',             2),
                                            ('VCATCH',              3),
                                            ('EXTERNAL',            4),
                                            ('PMU',                 5),
                                            ]),
            AReg32('MMFAR',         0xD34, [('ADDRESS',             0,  31),
                                            ]),
            AReg32('BFAR',          0xD38, [('ADDRESS',             0,  31),
                                            ]),
            AReg32('AFSR',          0xD3C),
            AReg32('CPACR',         0xD88, [('CP0',                 0,  1),
                                            ('CP1',                 2,  3),
                                            ('CP2',                 4,  5),
                                            ('CP3',                 6,  7),
                                            ('CP4',                 8,  9),
                                            ('CP5',                 10, 11),
                                            ('CP6',                 12, 13),
                                            ('CP7',                 14, 15),
                                            ('CP10',                20, 21),
                                            ('CP11',                22, 23),
                                            ]),
            AReg32('DHCSR',         0xDF0, [('C_DEBUGEN',           0),
                                            ('C_HALT',              1),
                                            ('C_STEP',              2),
                                            ('C_MASKINTS',          3),
                                            ('C_SNAPSTALL',         5),
                                            ('C_PMOV',              6),
                                            ('S_REGRDY',            16),
                                            ('S_HALT',              17),
                                            ('S_SLEEP',             18),
                                            ('S_LOCKUP',            19),
                                            ('S_SDE',               20),
                                            ('S_NSUIDE',            21),
                                            ('S_SUIDE',             22),
                                            ('S_FPD',               23),
                                            ('S_RETIRE_ST',         24),
                                            ('S_RESET_ST',          25),
                                            ('S_RESTART_ST',        26),
                                            ]),
            AReg32W('DCRSR',        0xDF4, [('REGSEL',              0,  7),
                                            ('REGWnR',              16),
                                            ]),
            AReg32('DCRDR',         0xDF8, [('DBGTMP',              0,  31),
                                            ]),
            AReg32('DEMCR',         0xDFC, [('VC_CORERESET',        0),
                                            ('VC_MMERR',            4),
                                            ('VC_NOCPERR',          5),
                                            ('VC_CHKERR',           6),
                                            ('VC_STATEERR',         7),
                                            ('VC_BUSERR',           8),
                                            ('VC_INTERR',           9),
                                            ('VC_HARDERR',          10),
                                            ('VC_SFERR',            11),
                                            ('MON_EN',              16),
                                            ('MON_PEND',            17),
                                            ('MON_STEP',            18),
                                            ('MON_REQ',             19),
                                            ('SDME',                20),
                                            ('UMON_EN',             21),
                                            ('MONPRKEY',            23),
                                            ('TRCENA',              24),
                                            ]),
            AReg32('DSCEMCR',       0xE00, [('SET_MON_PEND',        1),
                                            ('SET_MON_REQ',         3),
                                            ('CLR_MON_PEND',        17),
                                            ('CLR_MON_REQ',         19),
                                            ]),
            AReg32('DAUTHCTRL',     0xE04, [('SPIDENSEL',           0),
                                            ('INTSPIDEN',           1),
                                            ('SPNIDENSEL',          2),
                                            ('INTSPNIDEN',          3),
                                            ('FSDMA',               8),
                                            ('UIDAPEN',             9),
                                            ('UIDEN',               10),
                                            ]),
            AReg32('DSCSR',         0xE08, [('SBRSELEN',            0),
                                            ('SBRSEL',              1),
                                            ('CDS',                 16),
                                            ('CDSKEY',              17),
                                            ]),
            ]

    def __init__(self, component, subtype):
        super().__init__(component, subtype, SCS.REGS, CORE_REGISTERS)

        # Enable DEMCR.TRCENA so we can probe further.
        self._DEMCR.TRCENA = 1
