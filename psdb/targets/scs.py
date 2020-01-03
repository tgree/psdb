# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from .device import Device, Reg32, Reg32R, Reg32W


class SCS(Device):
    '''
    Driver for Cortex System Control Space.
    '''
    REGS = [Reg32 ('MCR',    0x000),
            Reg32R('ICTR',   0x004),
            Reg32 ('ACTLR',  0x008),
            Reg32R('CPUID',  0xD00),
            Reg32 ('ICSR',   0xD04),
            Reg32 ('VTOR',   0xD08),
            Reg32 ('AIRCR',  0xD0C),
            Reg32 ('SCR',    0xD10),
            Reg32 ('CCR',    0xD14),
            Reg32 ('SHPR1',  0xD18),
            Reg32 ('SHPR2',  0xD1C),
            Reg32 ('SHPR3',  0xD20),
            Reg32 ('SHCSR',  0xD24),
            Reg32 ('CFSR',   0xD28),
            Reg32 ('HFSR',   0xD2C),
            Reg32 ('DFSR',   0xD30),
            Reg32 ('MMFAR',  0xD34),
            Reg32 ('BFAR',   0xD38),
            Reg32 ('AFSR',   0xD3C),
            Reg32 ('CPACR',  0xD88),
            Reg32 ('DHCSR',  0xDF0),
            Reg32W('DCRSR',  0xDF4),
            #Reg32 ('DCRDR',  0xDF8),
            Reg32 ('DEMCR',  0xDFC),
            ]

    def __init__(self, target, ap, name, addr):
        super(SCS, self).__init__(target, ap, addr, name, SCS.REGS)
