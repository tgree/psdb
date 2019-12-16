# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from builtins import range

from ..device import Device, Reg32, Reg32R


class ADC(Device):
    '''
    Driver for the STM32G4 ADC.
    '''
    PER_ADC_REGS = [(Reg32,  'ISR',     0x00),
                    (Reg32,  'IER',     0x04),
                    (Reg32,  'CR',      0x08),
                    (Reg32,  'CFGR',    0x0C),
                    (Reg32,  'CFGR2',   0x10),
                    (Reg32,  'SMPR1',   0x14),
                    (Reg32,  'SMPR2',   0x18),
                    (Reg32,  'TR1',     0x20),
                    (Reg32,  'TR2',     0x24),
                    (Reg32,  'TR3',     0x28),
                    (Reg32,  'SQR1',    0x30),
                    (Reg32,  'SQR2',    0x34),
                    (Reg32,  'SQR3',    0x38),
                    (Reg32,  'SQR4',    0x3C),
                    (Reg32R, 'DR',      0x40),
                    (Reg32,  'JSQR',    0x4C),
                    (Reg32,  'OFR1',    0x60),
                    (Reg32,  'OFR2',    0x64),
                    (Reg32,  'OFR3',    0x68),
                    (Reg32,  'OFR4',    0x6C),
                    (Reg32R, 'JDR1',    0x80),
                    (Reg32R, 'JDR2',    0x84),
                    (Reg32R, 'JDR3',    0x88),
                    (Reg32R, 'JDR4',    0x8C),
                    (Reg32,  'AWD2CR',  0xA0),
                    (Reg32,  'AWD3CR',  0xA4),
                    (Reg32,  'DIFSEL',  0xB0),
                    (Reg32,  'CALFACT', 0xB4),
                    (Reg32,  'GCOMP',   0xC0),
                    ]
    COM_ADC_REGS = [Reg32R('CSR', 0x00),
                    Reg32 ('CCR', 0x08),
                    Reg32R('CDR', 0x0C),
                    ]

    def __init__(self, target, name, addr, first_adc, nadcs):
        regs = []
        for i in range(nadcs):
            base = 0x100*i
            regs += [cls(_name + ('_%u' % (first_adc + i)), base + offset)
                     for cls, _name, offset in ADC.PER_ADC_REGS]
        regs += ADC.COM_ADC_REGS

        super(ADC, self).__init__(target, addr, name, regs)
