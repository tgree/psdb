# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .target import (Target, MemRegion)
from . import msp432
from . import stm32h7
from . import stm32g0
from . import stm32g4
from . import stm32wb55


__all__ = ['Target',
           'MemRegion',
           ]

TARGETS = [msp432.MSP432P401,
           stm32h7.STM32H7,
           stm32h7.STM32H7_DP,
           stm32g0.STM32G0,
           stm32g4.STM32G4,
           stm32wb55.STM32WB55,
           ]


def probe(db):
    for t in TARGETS:
        device = t.probe(db)
        if device:
            return device
    return None
