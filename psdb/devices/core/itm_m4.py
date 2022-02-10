# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
from psdb.devices import AReg32
from .cortex_subdevice import CortexSubDevice


class ITM(CortexSubDevice):
    '''
    Driver for the Instrumentation Trace Macrocell (IWT) variant found on the
    Cortex-M4.

    Note: The LAR/LSR registers are present (at least, on the STM32G4) even
    though they are not documented anywhere in ARMv7-M or in the Cortex-M4 TRM.
    The registers are documented in Cortex-M7 and Cortex-M33 TRMs.  They are
    not documented in the Cortex-M3 TRM either, although I don't know if they
    are present on an M3.
    '''
    REGS = [AReg32('STIM0',             0x000),
            AReg32('STIM1',             0x004),
            AReg32('STIM2',             0x008),
            AReg32('STIM3',             0x00C),
            AReg32('STIM4',             0x010),
            AReg32('STIM5',             0x014),
            AReg32('STIM6',             0x018),
            AReg32('STIM7',             0x01C),
            AReg32('STIM8',             0x020),
            AReg32('STIM9',             0x024),
            AReg32('STIM10',            0x028),
            AReg32('STIM11',            0x02C),
            AReg32('STIM12',            0x030),
            AReg32('STIM13',            0x034),
            AReg32('STIM14',            0x038),
            AReg32('STIM15',            0x03C),
            AReg32('STIM16',            0x040),
            AReg32('STIM17',            0x044),
            AReg32('STIM18',            0x048),
            AReg32('STIM19',            0x04C),
            AReg32('STIM20',            0x050),
            AReg32('STIM21',            0x054),
            AReg32('STIM22',            0x058),
            AReg32('STIM23',            0x05C),
            AReg32('STIM24',            0x060),
            AReg32('STIM25',            0x064),
            AReg32('STIM26',            0x068),
            AReg32('STIM27',            0x06C),
            AReg32('STIM28',            0x070),
            AReg32('STIM29',            0x074),
            AReg32('STIM30',            0x078),
            AReg32('STIM31',            0x07C),
            AReg32('TER',               0xE00, [('STIMENA0',    0),
                                                ('STIMENA1',    1),
                                                ('STIMENA2',    2),
                                                ('STIMENA3',    3),
                                                ('STIMENA4',    4),
                                                ('STIMENA5',    5),
                                                ('STIMENA6',    6),
                                                ('STIMENA7',    7),
                                                ('STIMENA8',    8),
                                                ('STIMENA9',    9),
                                                ('STIMENA10',   10),
                                                ('STIMENA11',   11),
                                                ('STIMENA12',   12),
                                                ('STIMENA13',   13),
                                                ('STIMENA14',   14),
                                                ('STIMENA15',   15),
                                                ('STIMENA16',   16),
                                                ('STIMENA17',   17),
                                                ('STIMENA18',   18),
                                                ('STIMENA19',   19),
                                                ('STIMENA20',   20),
                                                ('STIMENA21',   21),
                                                ('STIMENA22',   22),
                                                ('STIMENA23',   23),
                                                ('STIMENA24',   24),
                                                ('STIMENA25',   25),
                                                ('STIMENA26',   26),
                                                ('STIMENA27',   27),
                                                ('STIMENA28',   28),
                                                ('STIMENA29',   29),
                                                ('STIMENA30',   30),
                                                ('STIMENA31',   31),
                                                ]),
            AReg32('TPR',               0xE40, [('PRIVMASK',    0,  3),
                                                ]),
            AReg32('TCR',               0xE80, [('ITMENA',      0),
                                                ('TSENA',       1),
                                                ('SYNCENA',     2),
                                                ('TXENA',       3),
                                                ('SWOENA',      4),
                                                ('TSPrescale',  8,  9),
                                                ('GTSFREQ',     10, 11),
                                                ('TraceBusID',  16, 22),
                                                ('BUSY',        23),
                                                ]),
            AReg32('LAR',               0xFB0, [('KEY',         0,  31),
                                                ]),
            AReg32('LSR',               0xFB4, [('SLI',         0),
                                                ('SLK',         1),
                                                ('nTT',         2),
                                                ]),
            ]

    def __init__(self, component, subtype):
        super().__init__('ITM', ITM.REGS, component, subtype)
