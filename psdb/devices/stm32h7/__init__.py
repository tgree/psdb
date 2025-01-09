# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from .flash_2x_3x import FLASH_2x_3x
from .flash_dp import FLASH_DP
from .flash_up import FLASH_UP
from .pwr import PWR
from .pwr_2x_3x import PWR_2x_3x
from .rcc import RCC
from .rcc_2x_3x import RCC_2x_3x
from .tim6 import TIM6
from .tim15 import TIM15
from .tim17 import TIM17
from .tim2_5 import TIM2_5
from .syscfg import SYSCFG
from .art import ART
from .opamp import OPAMP
from .spi import SPI

TIM7 = TIM6


__all__ = ['ART',
           'FLASH_2x_3x',
           'FLASH_DP',
           'FLASH_UP',
           'PWR',
           'PWR_2x_3x',
           'RCC',
           'RCC_2x_3x',
           'TIM6',
           'TIM7',
           'TIM15',
           'TIM17',
           'TIM2_5',
           'SYSCFG',
           'OPAMP',
           'SPI',
           ]
