# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import time
import datetime

from ..device import Device, Reg32


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
    Driver for the STM32G4 real-time clock device (RTC).
    '''
    REGS = [Reg32('TR',         0x00,  [('SU',              4),
                                        ('ST',              3),
                                        ('',                1),
                                        ('MNU',             4),
                                        ('MNT',             3),
                                        ('',                1),
                                        ('HU',              4),
                                        ('HT',              2),
                                        ('PM',              1),
                                        ]),
            Reg32('DR',         0x04,  [('DU',              4),
                                        ('DT',              2),
                                        ('',                2),
                                        ('MU',              4),
                                        ('MT',              1),
                                        ('WDU',             3),
                                        ('YU',              4),
                                        ('YT',              4),
                                        ]),
            Reg32('SSR',        0x08,  [('SS',              16),
                                        ]),
            Reg32('ICSR',       0x0C,  [('ALRAWF',          1),
                                        ('ALRBWF',          1),
                                        ('WUTWF',           1),
                                        ('SHPF',            1),
                                        ('INITS',           1),
                                        ('RSF',             1),
                                        ('INITF',           1),
                                        ('INIT',            1),
                                        ('',                8),
                                        ('RECALPF',         1),
                                        ]),
            Reg32('PRER',       0x10,  [('PREDIV_S',        15),
                                        ('',                1),
                                        ('PREDIV_A',        7),
                                        ]),
            Reg32('WUTR',       0x14,  [('WUT',             16),
                                        ]),
            Reg32('CR',         0x18,  [('WUCKSEL',         3),
                                        ('TSEDGE',          1),
                                        ('REFCKON',         1),
                                        ('BYPSHA',          1),
                                        ('FMT',             1),
                                        ('',                1),
                                        ('ALRAE',           1),
                                        ('ALRBE',           1),
                                        ('WUTE',            1),
                                        ('TSE',             1),
                                        ('ALRAIE',          1),
                                        ('ALRBIE',          1),
                                        ('WUTIE',           1),
                                        ('TSIE',            1),
                                        ('ADD1H',           1),
                                        ('SUB1H',           1),
                                        ('BKP',             1),
                                        ('COSEL',           1),
                                        ('POL',             1),
                                        ('OSEL',            2),
                                        ('COE',             1),
                                        ('ITSE',            1),
                                        ('TAMPTS',          1),
                                        ('TAMPOE',          1),
                                        ('',                2),
                                        ('TAMPALRM_PU',     1),
                                        ('TAMPALRM_TYPE',   1),
                                        ('OUT2_EN',         1),
                                        ]),
            Reg32('WPR',        0x24,  [('KEY',             8),
                                        ]),
            Reg32('CALR',       0x28,  [('CALM',            9),
                                        ('',                4),
                                        ('CALW16',          1),
                                        ('CALW8',           1),
                                        ('CALP',            1),
                                        ]),
            Reg32('SHIFTR',     0x2C,  [('SUBFS',           15),
                                        ('',                16),
                                        ('ADD1S',           1),
                                        ]),
            Reg32('TSTR',       0x30,  [('SU',              4),
                                        ('ST',              3),
                                        ('',                1),
                                        ('MNU',             4),
                                        ('MNT',             3),
                                        ('',                1),
                                        ('HU',              4),
                                        ('HT',              2),
                                        ('PM',              1),
                                        ]),
            Reg32('TSDR',       0x34,  [('DU',              4),
                                        ('DT',              2),
                                        ('',                2),
                                        ('MU',              4),
                                        ('MT',              1),
                                        ('WDU',             3),
                                        ]),
            Reg32('TSSSR',      0x38,  [('SS',              16),
                                        ]),
            Reg32('ALRMAR',     0x40,  [('SU',              4),
                                        ('ST',              3),
                                        ('MSK1',            1),
                                        ('MNU',             4),
                                        ('MNT',             3),
                                        ('MSK2',            1),
                                        ('HU',              4),
                                        ('HT',              2),
                                        ('PM',              1),
                                        ('MSK3',            1),
                                        ('DU',              4),
                                        ('DT',              2),
                                        ('WDSEL',           1),
                                        ('MSK4',            1),
                                        ]),
            Reg32('ALRMASSR',   0x44,  [('SS',              15),
                                        ('',                9),
                                        ('MASKSS',          4),
                                        ]),
            Reg32('ALRMBR',     0x48,  [('SU',              4),
                                        ('ST',              3),
                                        ('MSK1',            1),
                                        ('MNU',             4),
                                        ('MNT',             3),
                                        ('MSK2',            1),
                                        ('HU',              4),
                                        ('HT',              2),
                                        ('PM',              1),
                                        ('MSK3',            1),
                                        ('DU',              4),
                                        ('DT',              2),
                                        ('WDSEL',           1),
                                        ('MSK4',            1),
                                        ]),
            Reg32('ALRMBSSR',   0x4C,  [('SS',              15),
                                        ('',                9),
                                        ('MASKSS',          4),
                                        ]),
            Reg32('SR',         0x50,  [('ALRAF',           1),
                                        ('ALRBF',           1),
                                        ('WUTF',            1),
                                        ('TSF',             1),
                                        ('TSOVF',           1),
                                        ('ITSF',            1),
                                        ]),
            Reg32('MISR',       0x54,  [('ALRAMF',          1),
                                        ('ALRBMF',          1),
                                        ('WUTMF',           1),
                                        ('TSMF',            1),
                                        ('TSOVMF',          1),
                                        ('ITSMF',           1),
                                        ]),
            Reg32('SCR',        0x5C,  [('CALRAF',          1),
                                        ('CALRBF',          1),
                                        ('CWUTF',           1),
                                        ('CTSF',            1),
                                        ('CTSOVF',          1),
                                        ('CITSF',           1),
                                        ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(RTC, self).__init__(target, ap, addr, name, RTC.REGS, **kwargs)

    def _rtc_unlocked(self):
        return UnlockedContextManager(self)

    def init(self):
        with self._rtc_unlocked():
            self._ICSR.INIT = 1
            while self._ICSR.INITF != 1:
                time.sleep(0.001)

            self._PRER.PREDIV_A = 127
            self._PRER.PREDIV_S = 255

            d   = datetime.datetime.now()
            yt  = (d.year // 10)
            yu  = (d.year % 10)
            wdu = (d.weekday() + 1)
            mt  = (d.month // 10)
            mu  = (d.month % 10)
            dt  = (d.day // 10)
            du  = (d.day % 10)
            ht  = (d.hour // 10)
            hu  = (d.hour % 10)
            mnt = (d.minute // 10)
            mnu = (d.minute % 10)
            st  = (d.second // 10)
            su  = (d.second % 10)
            self._CR.FMT = 0
            self._TR     = ((ht  << 20) |
                            (hu  << 16) |
                            (mnt << 12) |
                            (mnu <<  8) |
                            (st  <<  4) |
                            (su  <<  0))
            self._DR     = ((yt  << 20) |
                            (yu  << 16) |
                            (wdu << 13) |
                            (mt  << 12) |
                            (mu  <<  8) |
                            (dt  <<  4) |
                            (du  <<  0))

            self._ICSR.INIT = 0
