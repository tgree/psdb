# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32W


class RCC(Device):
    '''
    Driver for STM32H745 RCC device.
    '''
    REGS = [Reg32W('CR',    0x000,   [('HSION',         1),
                                      ('HSIKERON',      1),
                                      ('HSIRDY',        1),
                                      ('HSIDIV',        2),
                                      ('HSIDIVF',       1),
                                      ('',              1),
                                      ('CSION',         1),
                                      ('CSIRDY',        1),
                                      ('CSIKERON',      1),
                                      ('',              2),
                                      ('HSI48ON',       1),
                                      ('HSI48RDY',      1),
                                      ('D1CKRDY',       1),
                                      ('D2CKRDY',       1),
                                      ('HSEON',         1),
                                      ('HSERDY',        1),
                                      ('HSEBYP',        1),
                                      ('HSECSSON',      1),
                                      ('',              4),
                                      ('PLL1ON',        1),
                                      ('PLL1RDY',       1),
                                      ('PLL2ON',        1),
                                      ('PLL2RDY',       1),
                                      ('PLL3ON',        1),
                                      ('PLL3RDY',       1),
                                      ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(RCC, self).__init__(target, ap, addr, name, RCC.REGS, **kwargs)
