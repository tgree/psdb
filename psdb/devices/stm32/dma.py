# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class DMA(Device):
    '''
    Driver for the STM32G4 DMA device.
    '''
    REGS = [Reg32('ISR',    0x000),
            Reg32('IFCR',   0x004),
            Reg32('CCR1',   0x008),
            Reg32('CNDTR1', 0x00C),
            Reg32('CPAR1',  0x010),
            Reg32('CMAR1',  0x014),
            Reg32('CCR2',   0x01C),
            Reg32('CNDTR2', 0x020),
            Reg32('CPAR2',  0x024),
            Reg32('CMAR2',  0x028),
            Reg32('CCR3',   0x030),
            Reg32('CNDTR3', 0x034),
            Reg32('CPAR3',  0x038),
            Reg32('CMAR3',  0x03C),
            Reg32('CCR4',   0x044),
            Reg32('CNDTR4', 0x048),
            Reg32('CPAR4',  0x04C),
            Reg32('CMAR4',  0x050),
            Reg32('CCR5',   0x058),
            Reg32('CNDTR5', 0x05C),
            Reg32('CPAR5',  0x060),
            Reg32('CMAR5',  0x064),
            Reg32('CCR6',   0x06C),
            Reg32('CNDTR6', 0x070),
            Reg32('CPAR6',  0x074),
            Reg32('CMAR6',  0x078),
            Reg32('CCR7',   0x080),
            Reg32('CNDTR7', 0x084),
            Reg32('CPAR7',  0x088),
            Reg32('CMAR7',  0x08C),
            Reg32('CCR8',   0x094),
            Reg32('CNDTR8', 0x098),
            Reg32('CPAR8',  0x09C),
            Reg32('CMAR8',  0x0A0),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, DMA.REGS, **kwargs)


class DMA_DBM(Device):
    '''
    Driver for the STM32H7 DMA device.
    '''
    REGS = [Reg32('LISR',   0x000),
            Reg32('HISR',   0x004),
            Reg32('LIFCR',  0x008),
            Reg32('HIFCR',  0x00C),
            Reg32('S0CR',   0x010 + 0x18*0,    [('EN',          1),
                                                ('DMEIE',       1),
                                                ('TEIE',        1),
                                                ('HTIE',        1),
                                                ('TCIE',        1),
                                                ('PFCTRL',      1),
                                                ('DIR',         2),
                                                ('CIRC',        1),
                                                ('PINC',        1),
                                                ('MINC',        1),
                                                ('PSIZE',       2),
                                                ('MSIZE',       2),
                                                ('PINCOS',      1),
                                                ('PL',          2),
                                                ('DBM',         1),
                                                ('CT',          1),
                                                ('TRBUFF',      1),
                                                ('PBURST',      2),
                                                ('MBURST',      2),
                                                ]),
            Reg32('S0NDTR', 0x014 + 0x18*0),
            Reg32('S0PAR',  0x018 + 0x18*0),
            Reg32('S0M0AR', 0x01C + 0x18*0),
            Reg32('S0M1AR', 0x020 + 0x18*0),
            Reg32('S0FCR',  0x024 + 0x18*0,    [('FTH',         2),
                                                ('DMDIS',       1),
                                                ('FS',          3),
                                                ('',            1),
                                                ('FEIE',        1),
                                                ]),
            Reg32('S1CR',   0x010 + 0x18*1),
            Reg32('S1NDTR', 0x014 + 0x18*1),
            Reg32('S1PAR',  0x018 + 0x18*1),
            Reg32('S1M0AR', 0x01C + 0x18*1),
            Reg32('S1M1AR', 0x020 + 0x18*1),
            Reg32('S1FCR',  0x024 + 0x18*1),
            Reg32('S2CR',   0x010 + 0x18*2),
            Reg32('S2NDTR', 0x014 + 0x18*2),
            Reg32('S2PAR',  0x018 + 0x18*2),
            Reg32('S2M0AR', 0x01C + 0x18*2),
            Reg32('S2M1AR', 0x020 + 0x18*2),
            Reg32('S2FCR',  0x024 + 0x18*2),
            Reg32('S3CR',   0x010 + 0x18*3),
            Reg32('S3NDTR', 0x014 + 0x18*3),
            Reg32('S3PAR',  0x018 + 0x18*3),
            Reg32('S3M0AR', 0x01C + 0x18*3),
            Reg32('S3M1AR', 0x020 + 0x18*3),
            Reg32('S3FCR',  0x024 + 0x18*3),
            Reg32('S4CR',   0x010 + 0x18*4),
            Reg32('S4NDTR', 0x014 + 0x18*4),
            Reg32('S4PAR',  0x018 + 0x18*4),
            Reg32('S4M0AR', 0x01C + 0x18*4),
            Reg32('S4M1AR', 0x020 + 0x18*4),
            Reg32('S4FCR',  0x024 + 0x18*4),
            Reg32('S5CR',   0x010 + 0x18*5),
            Reg32('S5NDTR', 0x014 + 0x18*5),
            Reg32('S5PAR',  0x018 + 0x18*5),
            Reg32('S5M0AR', 0x01C + 0x18*5),
            Reg32('S5M1AR', 0x020 + 0x18*5),
            Reg32('S5FCR',  0x024 + 0x18*5),
            Reg32('S6CR',   0x010 + 0x18*6),
            Reg32('S6NDTR', 0x014 + 0x18*6),
            Reg32('S6PAR',  0x018 + 0x18*6),
            Reg32('S6M0AR', 0x01C + 0x18*6),
            Reg32('S6M1AR', 0x020 + 0x18*6),
            Reg32('S6FCR',  0x024 + 0x18*6),
            Reg32('S7CR',   0x010 + 0x18*7),
            Reg32('S7NDTR', 0x014 + 0x18*7),
            Reg32('S7PAR',  0x018 + 0x18*7),
            Reg32('S7M0AR', 0x01C + 0x18*7),
            Reg32('S7M1AR', 0x020 + 0x18*7),
            Reg32('S7FCR',  0x024 + 0x18*7),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, DMA_DBM.REGS, **kwargs)
