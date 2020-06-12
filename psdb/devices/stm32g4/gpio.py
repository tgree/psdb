# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32, Reg32R, Reg32W


class GPIO(Device):
    '''
    Driver for a GPIO Port device.
    '''
    REGS = [Reg32 ('MODER',     0x00),
            Reg32 ('OTYPER',    0x04),
            Reg32 ('OSPEEDR',   0x08),
            Reg32 ('PUPDR',     0x0C),
            Reg32R('IDR',       0x10),
            Reg32 ('ODR',       0x14),
            Reg32W('BSRR',      0x18),
            Reg32 ('LCKR',      0x1C),
            Reg32 ('AFRL',      0x20),
            Reg32 ('AFRH',      0x24),
            Reg32 ('BRR',       0x28),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(GPIO, self).__init__(target, ap, addr, name, GPIO.REGS, **kwargs)
