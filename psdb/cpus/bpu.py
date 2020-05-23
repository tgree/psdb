# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from ..targets.device import Reg32, Reg32R, Reg32W
from .cortex_subdevice import CortexSubDevice


class BPU(CortexSubDevice):
    '''
    Driver for Cortex V6-M (M0+) Breakpoint Unit.
    '''
    REGS = [Reg32('BP_CTRL',    0x00,  [('ENABLE',      1),
                                        ('KEY',         1),
                                        ('',            2),
                                        ('NUM_CODE',    4),
                                        ]),
            Reg32('BP_COMP0',   0x08),
            Reg32('BP_COMP1',   0x0C),
            Reg32('BP_COMP2',   0x10),
            Reg32('BP_COMP3',   0x14),
            ]

    def __init__(self, component, subtype):
        super(BPU, self).__init__('BPU', BPU.REGS, component, subtype)
