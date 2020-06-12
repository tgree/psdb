# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32, Reg32R, Reg32W


class DMAMUX(Device):
    '''
    Driver for the STM32G4 DMAMUX device.
    '''
    REGS = [Reg32 ('C0CR',  0x000 +  0*0x04),
            Reg32 ('C1CR',  0x000 +  1*0x04),
            Reg32 ('C2CR',  0x000 +  2*0x04),
            Reg32 ('C3CR',  0x000 +  3*0x04),
            Reg32 ('C4CR',  0x000 +  4*0x04),
            Reg32 ('C5CR',  0x000 +  5*0x04),
            Reg32 ('C6CR',  0x000 +  6*0x04),
            Reg32 ('C7CR',  0x000 +  7*0x04),
            Reg32 ('C8CR',  0x000 +  8*0x04),
            Reg32 ('C9CR',  0x000 +  9*0x04),
            Reg32 ('C10CR', 0x000 + 10*0x04),
            Reg32 ('C11CR', 0x000 + 11*0x04),
            Reg32 ('C12CR', 0x000 + 12*0x04),
            Reg32 ('C13CR', 0x000 + 13*0x04),
            Reg32 ('C14CR', 0x000 + 14*0x04),
            Reg32 ('C15CR', 0x000 + 15*0x04),
            Reg32R('CSR',   0x080),
            Reg32W('CFR',   0x084),
            Reg32 ('RG0CR', 0x100 +  0*0x04),
            Reg32 ('RG1CR', 0x100 +  1*0x04),
            Reg32 ('RG2CR', 0x100 +  2*0x04),
            Reg32 ('RG3CR', 0x100 +  3*0x04),
            Reg32R('RGSR',  0x140),
            Reg32W('RGCFR', 0x144),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(DMAMUX, self).__init__(target, ap, addr, name, DMAMUX.REGS,
                                     **kwargs)
