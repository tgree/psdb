# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class DBGMCU(Device):
    '''
    Driver for the STM32G4 MCU debug component (DBGMCU).
    '''
    REGS = [Reg32('IDCODE',     0x00, [('DEV_ID',           12),
                                       ('',                 4),
                                       ('REV_ID',           16),
                                       ]),
            Reg32('CR',         0x04, [('DBG_SLEEP',        1),
                                       ('DBG_STOP',         1),
                                       ('DBG_STANDBY',      1),
                                       ('',                 2),
                                       ('TRACE_IOEN',       1),
                                       ('TRACE_MODE',       2),
                                       ]),
            Reg32('APB1FZR1',   0x08, [('DBG_TIM2_STOP',    1),
                                       ('DBG_TIM3_STOP',    1),
                                       ('DBG_TIM4_STOP',    1),
                                       ('DBG_TIM5_STOP',    1),
                                       ('DBG_TIM6_STOP',    1),
                                       ('DBG_TIM7_STOP',    1),
                                       ('',                 4),
                                       ('DBG_RTC_STOP',     1),
                                       ('DBG_WWDG_STOP',    1),
                                       ('DBG_IWDG_STOP',    1),
                                       ('',                 8),
                                       ('DBG_I2C1_STOP',    1),
                                       ('DBG_I2C2_STOP',    1),
                                       ('',                 7),
                                       ('DBG_I2C3_STOP',    1),
                                       ('DBG_LPTIM1_STOP',  1),
                                       ]),
            Reg32('APB1FZR2',   0x0C, [('',                 1),
                                       ('DBG_I2C4_STOP',    1),
                                       ]),
            Reg32('APB2FZR',    0x10, [('',                 11),
                                       ('DBG_TIM1_STOP',    1),
                                       ('',                 1),
                                       ('DBG_TIM8_STOP',    1),
                                       ('',                 2),
                                       ('DBG_TIM15_STOP',   1),
                                       ('DBG_TIM16_STOP',   1),
                                       ('DBG_TIM17_STOP',   1),
                                       ('',                 1),
                                       ('DBG_TIM20_STOP',   1),
                                       ('',                 5),
                                       ('DBG_HRTIM_STOP',   1),
                                       ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(DBGMCU, self).__init__(target, ap, addr, name, DBGMCU.REGS,
                                     **kwargs)
