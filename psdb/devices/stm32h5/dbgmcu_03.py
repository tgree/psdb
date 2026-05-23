# Copyright (c) 2020-2026 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32


class DBGMCU_03(Device):
    '''
    Driver for the STM32H503 MCU debug component (DBGMCU).
    '''
    REGS = [AReg32('IDCODE',        0x000, [('DEV_ID',            0, 11),
                                            ('REV_ID',           16, 31),
                                            ]),
            AReg32('CR',            0x004, [('DBG_STOP',          1),
                                            ('DBG_STANDBY',       2),
                                            ('TRACE_IOEN',        4),
                                            ('TRACE_EN',          5),
                                            ('TRACE_MODE',        6,  7),
                                            ('DCRT',              16),
                                            ]),
            AReg32('APB1LFZR',      0x008, [('DBG_TIM2_STOP',     0),
                                            ('DBG_TIM3_STOP',     1),
                                            ('DBG_TIM6_STOP',     4),
                                            ('DBG_TIM7_STOP',     5),
                                            ('DBG_WWDG_STOP',    11),
                                            ('DBG_IWDG_STOP',    12),
                                            ('DBG_I2C1_STOP',    21),
                                            ('DBG_I2C2_STOP',    22),
                                            ('DBG_I3C1_STOP',    23),
                                            ]),
            AReg32('APB1HFZR',      0x00C, [('DBG_LPTIM2_STOP',   5),
                                            ]),
            AReg32('APB2FZR',       0x010, [('DBG_TIM1_STOP',    11),
                                            ]),
            AReg32('APB3FZR',       0x014, [('DBG_I3C2_STOP',    12),
                                            ('DBG_LPTIM1_STOP',  17),
                                            ('DBG_RTC_STOP',     30),
                                            ]),
            AReg32('SR',            0x0FC, [('AP_PRESENT',        0, 15),
                                            ('AP_ENABLED',       16, 31),
                                            ]),
            AReg32('AUTH_HOST',     0x100, [('MESSAGE',           0, 31),
                                            ]),
            AReg32('AUTH_DEVICE',   0x104, [('MESSAGE',           0, 31),
                                            ]),
            AReg32('AUTH_ACK',      0x108, [('HOST_ACK',          0),
                                            ('DEV_ACK',           1),
                                            ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, DBGMCU_03.REGS, **kwargs)
