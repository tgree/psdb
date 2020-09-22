# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32, Reg32R, Reg32W


class DMAMUX(Device):
    '''
    Driver for the STM32 DMAMUX device.
    '''
    def __init__(self, target, ap, name, addr, nchans, nrgens, **kwargs):
        regs  = []
        regs += [Reg32('C%uCR' % i, 0x000 + i*0x04) for i in range(nchans)]
        regs += [Reg32R('CSR', 0x080),
                 Reg32W('CFR', 0x084)]
        regs += [Reg32('RG%uCR' % i, 0x100 + i*0x04) for i in range(nrgens)]
        regs += [Reg32R('RGSR',  0x140),
                 Reg32W('RGCFR', 0x144)]
        super(DMAMUX, self).__init__(target, ap, addr, name, regs, **kwargs)
