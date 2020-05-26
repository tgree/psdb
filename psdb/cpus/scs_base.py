# Copyright (c) 2019-2020 Phase Advanced Sensor Systems, Inc.
from ..targets.device import Reg32, Reg32R, Reg32W
from .cortex_subdevice import CortexSubDevice


class SCS(CortexSubDevice):
    '''
    Base class for Cortex V6-M (M0+) and V7-M (M4, M7) System Control Space
    devices.
    '''
    def __init__(self, component, subtype, dev_regs, core_regs):
        super(SCS, self).__init__('SCS', dev_regs, component, subtype)
        self.core_regs = core_regs

    def read_cpuid(self):
        return self._CPUID.read()
