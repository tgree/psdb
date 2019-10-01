# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .target import (Target, MemRegion)
from .device import Reg, MemDevice
from . import msp432


TARGETS = [msp432.MSP432P401]

def probe(db):
    for t in TARGETS:
        device = t.probe(db)
        if device:
            return device
    return None
