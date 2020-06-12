# Copyright (c) 2019-2020 Phase Advanced Sensor Systems, Inc.
from .cortex_subdevice import CortexSubDevice

import time
import collections


class SCS(CortexSubDevice):
    '''
    Base class for Cortex V6-M (M0+) and V7-M (M4, M7) System Control Space
    devices.
    '''
    def __init__(self, component, subtype, dev_regs, core_regs):
        super(SCS, self).__init__('SCS', dev_regs, component, subtype)
        self.core_regs = core_regs

        # Enable DHCSR.C_DEBUGEN so that we have debug control of the CPU.
        # Preserve the state of the other debug bits.
        bits        = self._DHCSR.read() & 0x0000000A
        self._DHCSR = (0xA05F0000 | bits | (1 << 0))

    def read_cpuid(self):
        return self._CPUID.read()

    def read_core_register(self, name):
        '''Reads one of the core registers.'''
        assert self.owner.is_halted()

        self._DCRSR = self.core_regs[name]
        while not self._DHCSR.S_REGRDY:
            time.sleep(0.001)
        return self._DCRDR.read()

    def read_core_registers(self):
        '''Reads all core registers.'''
        regs = collections.OrderedDict()
        for r in self.core_regs:
            regs[r] = self.read_core_register(r)
        return regs

    def write_core_register(self, v, name):
        '''Writes a single core register.'''
        assert self.owner.is_halted()

        self._DCRDR = v
        self._DCRSR = ((1<<16) | self.core_regs[name])
        while not self._DHCSR.S_REGRDY:
            time.sleep(0.001)

    def is_halted(self):
        return (self._DHCSR.S_HALT != 0)

    def halt(self):
        self._DHCSR = (0xA05F0000 | (1 << 1) | (1 << 0))
        while not self._DHCSR.S_HALT:
            time.sleep(0.001)

    def single_step(self):
        self._DHCSR = (0xA05F0000 | (1 << 3) | (1 << 2) | (1 << 0))
        while not self._DHCSR.S_HALT:
            time.sleep(0.001)

    def resume(self):
        self._DHCSR = (0xA05F0000 | (1 << 0))

    def enable_reset_vector_catch(self):
        assert self._DHCSR.read() & (1 << 0)
        self._DEMCR.VC_CORERESET = 1

    def disable_reset_vector_catch(self):
        assert self._DHCSR.read() & (1 << 0)
        self._DEMCR.VC_CORERESET = 0

    def trigger_aircr_local_reset(self):
        '''
        Uses the AIRCR register to trigger a local reset.  These resets the CPU
        but doesn't necessarily invalidate anything else.  In an MP system it
        may not even reset other CPUs.
        '''
        assert self._DHCSR.read() & (1 << 0)
        self._AIRCR = ((self._AIRCR.read() & 0x0000FFF8) | 0x05FA0004)

    def wait_aircr_local_reset_complete(self):
        while True:
            try:
                if not self._AIRCR.SYSRESETREQ:
                    break
                time.sleep(0.001)
            except Exception:
                pass

    def clear_reset_state(self):
        while self._DHCSR.S_RESET_ST:
            pass

    def wait_reset_state(self):
        while not self._DHCSR.S_RESET_ST:
            pass
