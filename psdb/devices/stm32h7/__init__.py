# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from .flash_dp import FLASH_DP
from .flash_up import FLASH_UP
from .pwr import PWR
from .rcc import RCC
from .tim6 import TIM6
from .tim15 import TIM15
from .tim17 import TIM17
from .tim2_5 import TIM2_5
from .syscfg import SYSCFG
from .art import ART
from .opamp import OPAMP

TIM7 = TIM6


__all__ = ['ART',
           'FLASH_DP',
           'FLASH_UP',
           'PWR',
           'RCC',
           'TIM6',
           'TIM7',
           'TIM15',
           'TIM17',
           'TIM2_5',
           'SYSCFG',
           'OPAMP',
           ]
