# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from ..targets.device import Reg32, Reg32R, Reg32W
from .cortex_subdevice import CortexSubDevice


class FPB(CortexSubDevice):
    '''
    Driver for Cortex V7-M (M4, M7) Flash Patch and Breakpoint unit.
    '''
    REGS = [Reg32('FP_CTRL',    0x00,  [('ENABLE',          1),
                                        ('KEY',             1),
                                        ('',                2),
                                        ('NUM_CODE[3:0]',   4),
                                        ('NUM_LIT',         4),
                                        ('NUM_CODE[6:4]',   3),
                                        ('',                13),
                                        ('REV',             4),
                                        ]),
            Reg32('FP_REMAP',   0x04,  [('',                5),
                                        ('REMAP',           24),
                                        ('RMPSPT',          1),
                                        ]),
            Reg32('FP_COMP0',   0x08),
            Reg32('FP_COMP1',   0x0C),
            Reg32('FP_COMP2',   0x10),
            Reg32('FP_COMP3',   0x14),
            Reg32('FP_COMP4',   0x18),
            Reg32('FP_COMP5',   0x1C),
            Reg32('FP_COMP6',   0x20),
            Reg32('FP_COMP7',   0x24),
            ]

    def __init__(self, component, subtype):
        super(FPB, self).__init__('FPB', FPB.REGS, component, subtype)
