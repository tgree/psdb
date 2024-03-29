# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import time

from ..device import Device, AReg32


class PWR(Device):
    '''
    Driver for the STM32U5 Power Control (PWR) device.
    '''
    REGS = [AReg32('CR1',           0x000, [('LPMS',            0,  2),
                                            ('RRSB1',           5),
                                            ('RRSB2',           6),
                                            ('ULPMEN',          7),
                                            ('SRAM1PD',         8),
                                            ('SRAM2PD',         9),
                                            ('SRAM3PD',         10),
                                            ('SRAM4PD',         11),
                                            ]),
            AReg32('CR2',           0x004, [('SRAM1PDS1',       0),
                                            ('SRAM1PDS2',       1),
                                            ('SRAM1PDS3',       2),
                                            ('SRAM2PDS1',       4),
                                            ('SRAM2PDS2',       5),
                                            ('SRAM4PDS',        6),
                                            ('ICRAMPDS',        8),
                                            ('DC1RAMPDS',       9),
                                            ('DMA2DRAMPDS',     10),
                                            ('PRAMPDS',         11),
                                            ('PKARAMPDS',       12),
                                            ('SRAM4FWU',        13),
                                            ('FLASHFWU',        14),
                                            ('SRAM3PDS1',       16),
                                            ('SRAM3PDS2',       17),
                                            ('SRAM3PDS3',       18),
                                            ('SRAM3PDS4',       19),
                                            ('SRAM3PDS5',       20),
                                            ('SRAM3PDS6',       21),
                                            ('SRAM3PDS7',       22),
                                            ('SRAM3PDS8',       23),
                                            ('SRDRUN',          31),
                                            ]),
            AReg32('CR3',           0x008, [('REGSEL',          1),
                                            ('FSTEN',           2),
                                            ]),
            AReg32('VOSR',          0x00C, [('BOOSTRDY',        14),
                                            ('VOSRDY',          15),
                                            ('VOS',             16, 17),
                                            ('BOOSTEN',         18),
                                            ]),
            AReg32('SVMCR',         0x010, [('PVDE',            4),
                                            ('PVDLS',           5,  7),
                                            ('UVMEN',           24),
                                            ('IO2VMEN',         25),
                                            ('AVM1EN',          26),
                                            ('AVM2EN',          27),
                                            ('USV',             28),
                                            ('IO2SV',           29),
                                            ('ASV',             30),
                                            ]),
            AReg32('WUCR1',         0x014, [('WUPEN1',          0),
                                            ('WUPEN2',          1),
                                            ('WUPEN3',          2),
                                            ('WUPEN4',          3),
                                            ('WUPEN5',          4),
                                            ('WUPEN6',          5),
                                            ('WUPEN7',          6),
                                            ('WUPEN8',          7),
                                            ]),
            AReg32('WUCR2',         0x018, [('WUPP1',           0),
                                            ('WUPP2',           1),
                                            ('WUPP3',           2),
                                            ('WUPP4',           3),
                                            ('WUPP5',           4),
                                            ('WUPP6',           5),
                                            ('WUPP7',           6),
                                            ('WUPP8',           7),
                                            ]),
            AReg32('WUCR3',         0x01C, [('WUSEL1',          0,  1),
                                            ('WUSEL2',          2,  3),
                                            ('WUSEL3',          4,  5),
                                            ('WUSEL4',          6,  7),
                                            ('WUSEL5',          8,  9),
                                            ('WUSEL6',          10, 11),
                                            ('WUSEL7',          12, 13),
                                            ('WUSEL8',          14, 15),
                                            ]),
            AReg32('BDCR1',         0x020, [('BREN',            0),
                                            ('MONEN',           4),
                                            ]),
            AReg32('BDCR2',         0x024, [('VBE',             0),
                                            ('VBRS',            1),
                                            ]),
            AReg32('DBPR',          0x028, [('DBP',             0),
                                            ]),
            AReg32('UCPDR',         0x02C, [('UCPD_DBDIS',      0),
                                            ('UCPD_STBY',       1),
                                            ]),
            AReg32('SECCFGR',       0x030, [('WUP1SEC',         0),
                                            ('WUP2SEC',         1),
                                            ('WUP3SEC',         2),
                                            ('WUP4SEC',         3),
                                            ('WUP5SEC',         4),
                                            ('WUP6SEC',         5),
                                            ('WUP7SEC',         6),
                                            ('WUP8SEC',         7),
                                            ('LPMSEC',          12),
                                            ('VDMSEC',          13),
                                            ('VBSEC',           14),
                                            ('APCSEC',          15),
                                            ]),
            AReg32('PRIVCFGR',      0x034, [('SPRIV',           0),
                                            ('NSPRIV',          1),
                                            ]),
            AReg32('SR',            0x038, [('CSSF',            0),
                                            ('STOPF',           1),
                                            ('SBF',             2),
                                            ]),
            AReg32('SVMSR',         0x03C, [('REGS',            1),
                                            ('PVDO',            4),
                                            ('ACTVOSRDY',       15),
                                            ('ACTVOS',          16, 17),
                                            ('VDDUSBRDY',       24),
                                            ('VDDIO2RDY',       25),
                                            ('VDDA1RDY',        26),
                                            ('VDDA2RDY',        27),
                                            ]),
            AReg32('BDSR',          0x040, [('VBATH',           1),
                                            ('TEMPL',           2),
                                            ('TEMPH',           3),
                                            ]),
            AReg32('WUSR',          0x044, [('WUF1',            0),
                                            ('WUF2',            1),
                                            ('WUF3',            2),
                                            ('WUF4',            3),
                                            ('WUF5',            4),
                                            ('WUF6',            5),
                                            ('WUF7',            6),
                                            ('WUF8',            7),
                                            ]),
            AReg32('WUSCR',         0x048, [('CWUF1',           0),
                                            ('CWUF2',           1),
                                            ('CWUF3',           2),
                                            ('CWUF4',           3),
                                            ('CWUF5',           4),
                                            ('CWUF6',           5),
                                            ('CWUF7',           6),
                                            ('CWUF8',           7),
                                            ]),
            AReg32('APCR',          0x04C, [('APC',             0),
                                            ]),
            AReg32('PUCRA',         0x050, [('PU0',             0),
                                            ('PU1',             1),
                                            ('PU2',             2),
                                            ('PU3',             3),
                                            ('PU4',             4),
                                            ('PU5',             5),
                                            ('PU6',             6),
                                            ('PU7',             7),
                                            ('PU8',             8),
                                            ('PU9',             9),
                                            ('PU10',            10),
                                            ('PU11',            11),
                                            ('PU12',            12),
                                            ('PU13',            13),
                                            ('PU15',            15),
                                            ]),
            AReg32('PDCRA',         0x054, [('PD0',             0),
                                            ('PD1',             1),
                                            ('PD2',             2),
                                            ('PD3',             3),
                                            ('PD4',             4),
                                            ('PD5',             5),
                                            ('PD6',             6),
                                            ('PD7',             7),
                                            ('PD8',             8),
                                            ('PD9',             9),
                                            ('PD10',            10),
                                            ('PD11',            11),
                                            ('PD12',            12),
                                            ('PD14',            14),
                                            ]),
            AReg32('PUCRB',         0x058, [('PU0',             0),
                                            ('PU1',             1),
                                            ('PU2',             2),
                                            ('PU3',             3),
                                            ('PU4',             4),
                                            ('PU5',             5),
                                            ('PU6',             6),
                                            ('PU7',             7),
                                            ('PU8',             8),
                                            ('PU9',             9),
                                            ('PU10',            10),
                                            ('PU11',            11),
                                            ('PU12',            12),
                                            ('PU13',            13),
                                            ('PU14',            14),
                                            ('PU15',            15),
                                            ]),
            AReg32('PDCRB',         0x05C, [('PD0',             0),
                                            ('PD1',             1),
                                            ('PD2',             2),
                                            ('PD3',             3),
                                            ('PD5',             5),
                                            ('PD6',             6),
                                            ('PD7',             7),
                                            ('PD8',             8),
                                            ('PD9',             9),
                                            ('PD10',            10),
                                            ('PD11',            11),
                                            ('PD12',            12),
                                            ('PD13',            13),
                                            ('PD14',            14),
                                            ('PD15',            15),
                                            ]),
            AReg32('PUCRC',         0x060, [('PU0',             0),
                                            ('PU1',             1),
                                            ('PU2',             2),
                                            ('PU3',             3),
                                            ('PU4',             4),
                                            ('PU5',             5),
                                            ('PU6',             6),
                                            ('PU7',             7),
                                            ('PU8',             8),
                                            ('PU9',             9),
                                            ('PU10',            10),
                                            ('PU11',            11),
                                            ('PU12',            12),
                                            ('PU13',            13),
                                            ('PU14',            14),
                                            ('PU15',            15),
                                            ]),
            AReg32('PDCRC',         0x064, [('PD0',             0),
                                            ('PD1',             1),
                                            ('PD2',             2),
                                            ('PD3',             3),
                                            ('PD4',             4),
                                            ('PD5',             5),
                                            ('PD6',             6),
                                            ('PD7',             7),
                                            ('PD8',             8),
                                            ('PD9',             9),
                                            ('PD10',            10),
                                            ('PD11',            11),
                                            ('PD12',            12),
                                            ('PD13',            13),
                                            ('PD14',            14),
                                            ('PD15',            15),
                                            ]),
            AReg32('PUCRD',         0x068, [('PU0',             0),
                                            ('PU1',             1),
                                            ('PU2',             2),
                                            ('PU3',             3),
                                            ('PU4',             4),
                                            ('PU5',             5),
                                            ('PU6',             6),
                                            ('PU7',             7),
                                            ('PU8',             8),
                                            ('PU9',             9),
                                            ('PU10',            10),
                                            ('PU11',            11),
                                            ('PU12',            12),
                                            ('PU13',            13),
                                            ('PU14',            14),
                                            ('PU15',            15),
                                            ]),
            AReg32('PDCRD',         0x06C, [('PD0',             0),
                                            ('PD1',             1),
                                            ('PD2',             2),
                                            ('PD3',             3),
                                            ('PD4',             4),
                                            ('PD5',             5),
                                            ('PD6',             6),
                                            ('PD7',             7),
                                            ('PD8',             8),
                                            ('PD9',             9),
                                            ('PD10',            10),
                                            ('PD11',            11),
                                            ('PD12',            12),
                                            ('PD13',            13),
                                            ('PD14',            14),
                                            ('PD15',            15),
                                            ]),
            AReg32('PUCRE',         0x070, [('PU0',             0),
                                            ('PU1',             1),
                                            ('PU2',             2),
                                            ('PU3',             3),
                                            ('PU4',             4),
                                            ('PU5',             5),
                                            ('PU6',             6),
                                            ('PU7',             7),
                                            ('PU8',             8),
                                            ('PU9',             9),
                                            ('PU10',            10),
                                            ('PU11',            11),
                                            ('PU12',            12),
                                            ('PU13',            13),
                                            ('PU14',            14),
                                            ('PU15',            15),
                                            ]),
            AReg32('PDCRE',         0x074, [('PD0',             0),
                                            ('PD1',             1),
                                            ('PD2',             2),
                                            ('PD3',             3),
                                            ('PD4',             4),
                                            ('PD5',             5),
                                            ('PD6',             6),
                                            ('PD7',             7),
                                            ('PD8',             8),
                                            ('PD9',             9),
                                            ('PD10',            10),
                                            ('PD11',            11),
                                            ('PD12',            12),
                                            ('PD13',            13),
                                            ('PD14',            14),
                                            ('PD15',            15),
                                            ]),
            AReg32('PUCRF',         0x078, [('PU0',             0),
                                            ('PU1',             1),
                                            ('PU2',             2),
                                            ('PU3',             3),
                                            ('PU4',             4),
                                            ('PU5',             5),
                                            ('PU6',             6),
                                            ('PU7',             7),
                                            ('PU8',             8),
                                            ('PU9',             9),
                                            ('PU10',            10),
                                            ('PU11',            11),
                                            ('PU12',            12),
                                            ('PU13',            13),
                                            ('PU14',            14),
                                            ('PU15',            15),
                                            ]),
            AReg32('PDCRF',         0x07C, [('PD0',             0),
                                            ('PD1',             1),
                                            ('PD2',             2),
                                            ('PD3',             3),
                                            ('PD4',             4),
                                            ('PD5',             5),
                                            ('PD6',             6),
                                            ('PD7',             7),
                                            ('PD8',             8),
                                            ('PD9',             9),
                                            ('PD10',            10),
                                            ('PD11',            11),
                                            ('PD12',            12),
                                            ('PD13',            13),
                                            ('PD14',            14),
                                            ('PD15',            15),
                                            ]),
            AReg32('PUCRG',         0x080, [('PU0',             0),
                                            ('PU1',             1),
                                            ('PU2',             2),
                                            ('PU3',             3),
                                            ('PU4',             4),
                                            ('PU5',             5),
                                            ('PU6',             6),
                                            ('PU7',             7),
                                            ('PU8',             8),
                                            ('PU9',             9),
                                            ('PU10',            10),
                                            ('PU11',            11),
                                            ('PU12',            12),
                                            ('PU13',            13),
                                            ('PU14',            14),
                                            ('PU15',            15),
                                            ]),
            AReg32('PDCRG',         0x084, [('PD0',             0),
                                            ('PD1',             1),
                                            ('PD2',             2),
                                            ('PD3',             3),
                                            ('PD4',             4),
                                            ('PD5',             5),
                                            ('PD6',             6),
                                            ('PD7',             7),
                                            ('PD8',             8),
                                            ('PD9',             9),
                                            ('PD10',            10),
                                            ('PD11',            11),
                                            ('PD12',            12),
                                            ('PD13',            13),
                                            ('PD14',            14),
                                            ('PD15',            15),
                                            ]),
            AReg32('PUCRH',         0x088, [('PU0',             0),
                                            ('PU1',             1),
                                            ('PU2',             2),
                                            ('PU3',             3),
                                            ('PU4',             4),
                                            ('PU5',             5),
                                            ('PU6',             6),
                                            ('PU7',             7),
                                            ('PU8',             8),
                                            ('PU9',             9),
                                            ('PU10',            10),
                                            ('PU11',            11),
                                            ('PU12',            12),
                                            ('PU13',            13),
                                            ('PU14',            14),
                                            ('PU15',            15),
                                            ]),
            AReg32('PDCRH',         0x08C, [('PD0',             0),
                                            ('PD1',             1),
                                            ('PD2',             2),
                                            ('PD3',             3),
                                            ('PD4',             4),
                                            ('PD5',             5),
                                            ('PD6',             6),
                                            ('PD7',             7),
                                            ('PD8',             8),
                                            ('PD9',             9),
                                            ('PD10',            10),
                                            ('PD11',            11),
                                            ('PD12',            12),
                                            ('PD13',            13),
                                            ('PD14',            14),
                                            ('PD15',            15),
                                            ]),
            AReg32('PUCRI',         0x090, [('PU0',             0),
                                            ('PU1',             1),
                                            ('PU2',             2),
                                            ('PU3',             3),
                                            ('PU4',             4),
                                            ('PU5',             5),
                                            ('PU6',             6),
                                            ('PU7',             7),
                                            ]),
            AReg32('PDCRI',         0x094, [('PD0',             0),
                                            ('PD1',             1),
                                            ('PD2',             2),
                                            ('PD3',             3),
                                            ('PD4',             4),
                                            ('PD5',             5),
                                            ('PD6',             6),
                                            ('PD7',             7),
                                            ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, PWR.REGS, **kwargs)

    def unlock_backup_domain(self):
        self._DBPR.DBP = 1
        while self._DBPR.DBP == 0:
            time.sleep(0.01)
