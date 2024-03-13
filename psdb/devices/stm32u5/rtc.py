# Copyright (c) 2020-2023 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32


class UnlockedContextManager:
    def __init__(self, rtc):
        self.rtc = rtc

    def __enter__(self):
        self.rtc._WPR = 0xFF
        self.rtc._WPR = 0xCA
        self.rtc._WPR = 0x53

    def __exit__(self, typ, value, traceback):
        self.rtc._WPR = 0xFF


class RTC(Device):
    '''
    Driver for the STM32U5 real-time clock device (RTC).
    '''
    REGS = [AReg32('TR',        0x00,  [('SU',              0,  3),
                                        ('ST',              4,  6),
                                        ('MNU',             8,  11),
                                        ('MNT',             12, 14),
                                        ('HU',              16, 19),
                                        ('HT',              20, 21),
                                        ('PM',              22),
                                        ]),
            AReg32('DR',        0x04,  [('DU',              0,  3),
                                        ('DT',              4,  5),
                                        ('MU',              8,  11),
                                        ('MT',              12),
                                        ('WDU',             13, 15),
                                        ('YU',              16, 19),
                                        ('YT',              20, 23),
                                        ]),
            AReg32('SSR',       0x08,  [('SS',              0,  31),
                                        ]),
            AReg32('ICSR',      0x0C,  [('WUTWF',           2),
                                        ('SHPF',            3),
                                        ('INITS',           4),
                                        ('RSF',             5),
                                        ('INITF',           6),
                                        ('INIT',            7),
                                        ('BIN',             8,  9),
                                        ('BCDU',            10, 12),
                                        ('RECALPF',         16),
                                        ]),
            AReg32('PRER',      0x10,  [('PREDIV_S',        0,  14),
                                        ('PREDIV_A',        16, 22),
                                        ]),
            AReg32('WUTR',      0x14,  [('WUT',             0,  15),
                                        ('WUTOCLR',         16, 31),
                                        ]),
            AReg32('CR',        0x18,  [('WUCKSEL',         0,  2),
                                        ('TSEDGE',          3),
                                        ('REFCKON',         4),
                                        ('BYPSHA',          5),
                                        ('FMT',             6),
                                        ('SSRUIE',          7),
                                        ('ALRAE',           8),
                                        ('ALRBE',           9),
                                        ('WUTE',            10),
                                        ('TSE',             11),
                                        ('ALRAIE',          12),
                                        ('ALRBIE',          13),
                                        ('WUTIE',           14),
                                        ('TSIE',            15),
                                        ('ADD1H',           16),
                                        ('SUB1H',           17),
                                        ('BKP',             18),
                                        ('COSEL',           19),
                                        ('POL',             20),
                                        ('OSEL',            21, 22),
                                        ('COE',             23),
                                        ('ITSE',            24),
                                        ('TAMPTS',          25),
                                        ('TAMPOE',          26),
                                        ('ALRAFCLR',        27),
                                        ('ALRBFCLR',        28),
                                        ('TAMPALRM_PU',     29),
                                        ('TAMPALRM_TYPE',   30),
                                        ('OUT2_EN',         31),
                                        ]),
            AReg32('PRIVCFGR',  0x1C,  [('ALRAPRIV',        0),
                                        ('ALRBPRIV',        1),
                                        ('WUTPRIV',         2),
                                        ('TSPRIV',          3),
                                        ('CALPRIV',         13),
                                        ('INITPRIV',        14),
                                        ('PRIV',            15),
                                        ]),
            AReg32('SECCFGR',   0x20,  [('ALRASEC',         0),
                                        ('ALRBSEC',         1),
                                        ('WUTSEC',          2),
                                        ('TSSEC',           3),
                                        ('CALSEC',          13),
                                        ('INITSEC',         14),
                                        ('SEC',             15),
                                        ]),
            AReg32('WPR',       0x24,  [('KEY',             0,  7),
                                        ]),
            AReg32('CALR',      0x28,  [('CALM',            0,  8),
                                        ('LPCAL',           12),
                                        ('CALW16',          13),
                                        ('CALW8',           14),
                                        ('CALP',            15),
                                        ]),
            AReg32('SHIFTR',    0x2C,  [('SUBFS',           0,  14),
                                        ('ADD1S',           31),
                                        ]),
            AReg32('TSTR',      0x30,  [('SU',              0,  3),
                                        ('ST',              4,  6),
                                        ('MNU',             8,  11),
                                        ('MNT',             12, 14),
                                        ('HU',              16, 19),
                                        ('HT',              20, 21),
                                        ('PM',              22),
                                        ]),
            AReg32('TSDR',      0x34,  [('DU',              0,  3),
                                        ('DT',              4,  5),
                                        ('MU',              8,  11),
                                        ('MT',              12),
                                        ('WDU',             13, 15),
                                        ]),
            AReg32('TSSSR',     0x38,  [('SS',              0,  31),
                                        ]),
            AReg32('ALRMAR',    0x40,  [('SU',              0,  3),
                                        ('ST',              4,  6),
                                        ('MSK1',            7),
                                        ('MNU',             8,  11),
                                        ('MNT',             12, 14),
                                        ('MSK2',            15),
                                        ('HU',              16, 19),
                                        ('HT',              20, 21),
                                        ('PM',              22),
                                        ('MSK3',            23),
                                        ('DU',              24, 27),
                                        ('DT',              28, 29),
                                        ('WDSEL',           30),
                                        ('MSK4',            31),
                                        ]),
            AReg32('ALRMASSR',  0x44,  [('SS',              0,  14),
                                        ('MASKSS',          24, 29),
                                        ('SSCLR',           31),
                                        ]),
            AReg32('ALRMBR',    0x48,  [('SU',              0,  3),
                                        ('ST',              4,  6),
                                        ('MSK1',            7),
                                        ('MNU',             8,  11),
                                        ('MNT',             12, 14),
                                        ('MSK2',            15),
                                        ('HU',              16, 19),
                                        ('HT',              20, 21),
                                        ('PM',              22),
                                        ('MSK3',            23),
                                        ('DU',              24, 27),
                                        ('DT',              28, 29),
                                        ('WDSEL',           30),
                                        ('MSK4',            31),
                                        ]),
            AReg32('ALRMBSSR',  0x4C,  [('SS',              0,  15),
                                        ('MASKSS',          24, 29),
                                        ('SSCLR',           31),
                                        ]),
            AReg32('SR',        0x50,  [('ALRAF',           0),
                                        ('ALRBF',           1),
                                        ('WUTF',            2),
                                        ('TSF',             3),
                                        ('TSOVF',           4),
                                        ('ITSF',            5),
                                        ('SSRUF',           6),
                                        ]),
            AReg32('MISR',      0x54,  [('ALRAMF',          0),
                                        ('ALRBMF',          1),
                                        ('WUTMF',           2),
                                        ('TSMF',            3),
                                        ('TSOVMF',          4),
                                        ('ITSMF',           5),
                                        ('SSRUMF',          6),
                                        ]),
            AReg32('SMISR',     0x58,  [('ALRAMF',          0),
                                        ('ALRBMF',          1),
                                        ('WUTMF',           2),
                                        ('TSMF',            3),
                                        ('TSOVMF',          4),
                                        ('ITSMF',           5),
                                        ('SSRUMF',          6),
                                        ]),
            AReg32('SCR',       0x5C,  [('CALRAF',          0),
                                        ('CALRBF',          1),
                                        ('CWUTF',           2),
                                        ('CTSF',            3),
                                        ('CTSOVF',          4),
                                        ('CITSF',           5),
                                        ('CUSSRUF',         6),
                                        ]),
            AReg32('ALRABINR',  0x70,  [('SS',              0,  31),
                                        ]),
            AReg32('ALRBBINR',  0x74,  [('SS',              0,  31),
                                        ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, RTC.REGS, **kwargs)

    def _rtc_unlocked(self):
        return UnlockedContextManager(self)