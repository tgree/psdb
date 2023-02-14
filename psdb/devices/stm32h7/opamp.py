# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32


class OPAMP(Device):
    '''
    Driver for the STM32H7 opamp device (OPAMP).
    '''
    REGS = [AReg32('OPAMP1_CSR',    0x000, [('OPAEN',           0),
                                            ('FORCE_VP',        1),
                                            ('VP_SEL',          2,  3),
                                            ('VM_SEL',          5,  6),
                                            ('OPAHSM',          8),
                                            ('CALON',           11),
                                            ('CALSEL',          12, 13),
                                            ('PGA_GAIN',        14, 17),
                                            ('USERTRIM',        18),
                                            ('TSTREF',          29),
                                            ('CALOUT',          30),
                                            ]),
            AReg32('OPAMP1_OTR',    0x004, [('TRIMOFFSETN',     0,  4),
                                            ('TRIMOFFSETP',     8,  12),
                                            ]),
            AReg32('OPAMP1_HSOTR',  0x008, [('TRIMHSOFFSETN',   0,  4),
                                            ('TRIMHSOFFSETP',   8,  12),
                                            ]),
            AReg32('OPAMP_OR',      0x00C),
            AReg32('OPAMP2_CSR',    0x010, [('OPAEN',           0),
                                            ('FORCE_VP',        1),
                                            ('VP_SEL',          2,  3),
                                            ('VM_SEL',          5,  6),
                                            ('OPAHSM',          8),
                                            ('CALON',           11),
                                            ('CALSEL',          12, 13),
                                            ('PGA_GAIN',        14, 17),
                                            ('USERTRIM',        18),
                                            ('TSTREF',          29),
                                            ('CALOUT',          30),
                                            ]),
            AReg32('OPAMP2_OTR',    0x014, [('TRIMOFFSETN',     0,  4),
                                            ('TRIMOFFSETP',     8,  12),
                                            ]),
            AReg32('OPAMP2_HSOTR',  0x018, [('TRIMHSOFFSETN',   0,  4),
                                            ('TRIMHSOFFSETP',   8,  12),
                                            ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, OPAMP.REGS, **kwargs)
