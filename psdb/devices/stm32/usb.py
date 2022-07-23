# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from psdb.devices import Device, Reg32


class USB(Device):
    '''
    Driver for the generic USB component found in the following MCUs:
        stm32g4
        stm32wb55
    '''
    REGS = [Reg32('EP0R',   0x00,  [('EA',          4),
                                    ('STAT_TX',     2),
                                    ('DTOG_TX',     1),
                                    ('CTR_TX',      1),
                                    ('EP_KIND',     1),
                                    ('EP_TYPE',     2),
                                    ('SETUP',       1),
                                    ('STAT_RX',     2),
                                    ('DTOG_RX',     1),
                                    ('CTR_RX',      1),
                                    ]),
            Reg32('EP1R',   0x04,  [('EA',          4),
                                    ('STAT_TX',     2),
                                    ('DTOG_TX',     1),
                                    ('CTR_TX',      1),
                                    ('EP_KIND',     1),
                                    ('EP_TYPE',     2),
                                    ('SETUP',       1),
                                    ('STAT_RX',     2),
                                    ('DTOG_RX',     1),
                                    ('CTR_RX',      1),
                                    ]),
            Reg32('EP2R',   0x08,  [('EA',          4),
                                    ('STAT_TX',     2),
                                    ('DTOG_TX',     1),
                                    ('CTR_TX',      1),
                                    ('EP_KIND',     1),
                                    ('EP_TYPE',     2),
                                    ('SETUP',       1),
                                    ('STAT_RX',     2),
                                    ('DTOG_RX',     1),
                                    ('CTR_RX',      1),
                                    ]),
            Reg32('EP3R',   0x0C,  [('EA',          4),
                                    ('STAT_TX',     2),
                                    ('DTOG_TX',     1),
                                    ('CTR_TX',      1),
                                    ('EP_KIND',     1),
                                    ('EP_TYPE',     2),
                                    ('SETUP',       1),
                                    ('STAT_RX',     2),
                                    ('DTOG_RX',     1),
                                    ('CTR_RX',      1),
                                    ]),
            Reg32('EP4R',   0x10,  [('EA',          4),
                                    ('STAT_TX',     2),
                                    ('DTOG_TX',     1),
                                    ('CTR_TX',      1),
                                    ('EP_KIND',     1),
                                    ('EP_TYPE',     2),
                                    ('SETUP',       1),
                                    ('STAT_RX',     2),
                                    ('DTOG_RX',     1),
                                    ('CTR_RX',      1),
                                    ]),
            Reg32('EP5R',   0x14,  [('EA',          4),
                                    ('STAT_TX',     2),
                                    ('DTOG_TX',     1),
                                    ('CTR_TX',      1),
                                    ('EP_KIND',     1),
                                    ('EP_TYPE',     2),
                                    ('SETUP',       1),
                                    ('STAT_RX',     2),
                                    ('DTOG_RX',     1),
                                    ('CTR_RX',      1),
                                    ]),
            Reg32('EP6R',   0x18,  [('EA',          4),
                                    ('STAT_TX',     2),
                                    ('DTOG_TX',     1),
                                    ('CTR_TX',      1),
                                    ('EP_KIND',     1),
                                    ('EP_TYPE',     2),
                                    ('SETUP',       1),
                                    ('STAT_RX',     2),
                                    ('DTOG_RX',     1),
                                    ('CTR_RX',      1),
                                    ]),
            Reg32('EP7R',   0x1C,  [('EA',          4),
                                    ('STAT_TX',     2),
                                    ('DTOG_TX',     1),
                                    ('CTR_TX',      1),
                                    ('EP_KIND',     1),
                                    ('EP_TYPE',     2),
                                    ('SETUP',       1),
                                    ('STAT_RX',     2),
                                    ('DTOG_RX',     1),
                                    ('CTR_RX',      1),
                                    ]),
            Reg32('CNTR',   0x40,  [('FRES',        1),
                                    ('PDWN',        1),
                                    ('LP_MODE',     1),
                                    ('FSUSP',       1),
                                    ('RESUME',      1),
                                    ('L1RESUME',    1),
                                    ('',            1),
                                    ('L1REQM',      1),
                                    ('ESOFM',       1),
                                    ('SOFM',        1),
                                    ('RESETM',      1),
                                    ('SUSPM',       1),
                                    ('WKUPM',       1),
                                    ('ERRM',        1),
                                    ('PMAOVRM',     1),
                                    ('CTRM',        1),
                                    ]),
            Reg32('ISTR',   0x44,  [('EP_ID',       4),
                                    ('DIR',         1),
                                    ('',            2),
                                    ('L1REQ',       1),
                                    ('ESOF',        1),
                                    ('SOF',         1),
                                    ('RESET',       1),
                                    ('SUSP',        1),
                                    ('WKUP',        1),
                                    ('ERR',         1),
                                    ('PMAOVR',      1),
                                    ('CTR',         1),
                                    ]),
            Reg32('FNR',    0x48,  [('FN',          11),
                                    ('LSOF',        2),
                                    ('LCK',         1),
                                    ('RXDM',        1),
                                    ('RXDP',        1),
                                    ]),
            Reg32('DADDR',  0x4C,  [('ADD',         7),
                                    ('EF',          1),
                                    ]),
            Reg32('BTABLE', 0x50,  [('',            3),
                                    ('BTABLE',      13),
                                    ]),
            Reg32('LPMCSR', 0x54,  [('LPMEN',       1),
                                    ('LPMACK',      1),
                                    ('',            1),
                                    ('REMWAKE',     1),
                                    ('BESL',        4),
                                    ]),
            Reg32('BCDR',   0x58,  [('BCDEN',       1),
                                    ('DCDEN',       1),
                                    ('PDEN',        1),
                                    ('SDEN',        1),
                                    ('DCDET',       1),
                                    ('PDET',        1),
                                    ('SDET',        1),
                                    ('PS2DET',      1),
                                    ('',            7),
                                    ('DPPU',        1),
                                    ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, USB.REGS, **kwargs)
