# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
from psdb.devices import AReg32, AReg32RS
from .coresight_0x9 import CoreSight9Device


class TPIU(CoreSight9Device):
    '''
    Driver for the specialized Trace Port Interface Unit (TPIU) found on
    Cortex-M4 MCUs.  This component is different from the standard CoreSight
    TPIU.

    The register descriptions for this TPIU implementation are spread across
    three different ARM manuals...
    '''
    REGS = [AReg32('SSPSR',             0x000, [('SWIDTH',          0,  31),
                                                ]),
            AReg32('CSPSR',             0x004, [('CWIDTH',          0,  31),
                                                ]),
            AReg32('ACPR',              0x010, [('PRESCALER',       0,  12),
                                                ]),
            AReg32('SPPR',              0x0F0, [('TXMODE',          0,  1),
                                                ]),
            AReg32('FFSR',              0x300, [('FlInProg',        0),
                                                ('FtStopped',       1),
                                                ('TCPresent',       2),
                                                ('FtNonStop',       3),
                                                ]),
            AReg32('FFCR',              0x304, [('EnFCont',         1),
                                                ('TrigIn',          8),
                                                ]),
            AReg32('FSCR',              0x308),  # Undocumented?
            AReg32('TRIGGER',           0xEE8, [('InputValue',      0),
                                                ]),
            AReg32RS('FIFO_DATA_0',     0xEEC, [('ETM_DATA_0',      0,  7),
                                                ('ETM_DATA_1',      8,  15),
                                                ('ETM_DATA_2',      16, 23),
                                                ('ETM_BYTE_COUNT',  24, 25),
                                                ('ETM_ATVALID',     26),
                                                ('ITM_BYTE_COUNT',  27, 28),
                                                ('ITM_ATVALID',     29),
                                                ]),
            AReg32('ITABCTR2',          0xEF0, [('ATREADY1_2',      0),
                                                ]),
            AReg32('ITABCTR0',          0xEF8, [('ATVALID1_2',      0),
                                                ]),
            AReg32RS('FIFO_DATA_1',     0xEFC, [('ITM_DATA_0',      0,  7),
                                                ('ITM_DATA_1',      8,  15),
                                                ('ITM_DATA_2',      16, 23),
                                                ('ETM_BYTE_COUNT',  24, 25),
                                                ('ETM_ATVALID',     26),
                                                ('ITM_BYTE_COUNT',  27, 28),
                                                ('ITM_ATVALID',     29),
                                                ]),
            AReg32('ITCTRL',            0xF00, [('MODE',            0,  1),
                                                ]),
            AReg32('DEVID',             0xFC8, [('NUM_TRACE_INPUTS',    0,  4),
                                                ('ASYNC_TRACECLKIN',    5),
                                                ('MIN_BUF_SIZE',        6,  8),
                                                ('TRACEDATA_CLK_MODES', 9),
                                                ('ASYNCSWO_MANCHESTER', 10),
                                                ('ASYNCSWO_NRZ',        11),
                                                ]),
            ]

    def __init__(self, component, subtype):
        super().__init__('TPIU', TPIU.REGS, component, subtype)
