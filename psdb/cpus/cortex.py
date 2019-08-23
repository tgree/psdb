# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb

import time
import collections


FLAG_HALTED   = (1<<0)

# The core registers and the selector value they map to in the DCRSR.
CORE_REGISTERS = collections.OrderedDict([
    ('r0',   0),  
    ('r1',   1),  
    ('r2',   2),  
    ('r3',   3),  
    ('r4',   4),  
    ('r5',   5),  
    ('r6',   6),  
    ('r7',   7),  
    ('r8',   8),  
    ('r9',   9),  
    ('r10',  10), 
    ('r11',  11), 
    ('r12',  12), 
    ('sp',   13), 
    ('lr',   14), 
    ('pc',   15), 
    ('xpsr', 16), 
])


class SystemControlBlock(psdb.component.Component):
    '''
    Component matcher for the Cortex SCB.  The SCB has registers that can be
    used to enable the DWT and ITM units; we need to enable them before
    allowing component probing to advance otherwise we will attempt to probe
    components that aren't enabled yet.
    '''
    def __init__(self, component, subtype):
        super(SystemControlBlock, self).__init__(component.parent, component.ap,
                                                 component.addr, subtype)
        self.write_demcr(0x01000000)

    def write_demcr(self, v):
        return self.ap.write_32(v, self.addr + 0xDFC)


class Cortex(psdb.component.Component):
    '''
    Base class component matcher for Cortex CPUs.  This is where we have common
    code for Cortex-M4 and Cortex-M7; there's no guarantee that this will work
    for any other Cortex model.
    '''
    def __init__(self, component, subtype):
        super(Cortex, self).__init__(component.parent, component.ap,
                                     component.addr, subtype)
        self._scb  = None
        self.flags = 0
        self.ap.db.cpus.append(self)

    @property
    def scb(self):
        if not self._scb:
            results = self.find_components_by_type(SystemControlBlock)
            assert results
            assert len(results) == 1
            self._scb = results[0]

        return self._scb

    def is_halted(self):
        return self.flags & FLAG_HALTED

    def read_8(self, addr):
        return self.ap.read_8(addr)

    def read_16(self, addr):
        return self.ap.read_16(addr)

    def read_32(self, addr):
        return self.ap.read_32(addr)

    def read_bulk(self, addr, size):
        return self.ap.read_bulk(addr, size)

    def read_aircr(self):
        return self.ap.read_32(self.scb.addr + 0xD0C)

    def read_dhcsr(self):
        return self.ap.read_32(self.scb.addr + 0xDF0)

    def read_dcrdr(self):
        return self.ap.read_32(self.scb.addr + 0xDF8)

    def read_demcr(self):
        return self.ap.read_32(self.scb.addr + 0xDFC)

    def _read_core_register(self, sel):
        assert self.flags & FLAG_HALTED
        assert sel < 128

        self.write_dcrsr(sel)
        while not (self.read_dhcsr() & (1<<16)):
            time.sleep(0.001)
        return self.read_dcrdr()

    def read_core_register(self, name):
        '''Reads a single core register.'''
        return self._read_core_register(CORE_REGISTERS[name])

    def read_core_registers(self):
        '''Read all of the core registers.'''
        regs = collections.OrderedDict()
        for r in CORE_REGISTERS:
            regs[r] = self.read_core_register(r)
        return regs

    def write_8(self, v, addr):
        self.ap.write_8(v, addr)

    def write_16(self, v, addr):
        self.ap.write_16(v, addr)

    def write_32(self, v, addr):
        self.ap.write_32(v, addr)

    def write_bulk(self, data, addr):
        self.ap.write_bulk(data, addr)

    def write_aircr(self, v):
        return self.ap.write_32(v, self.scb.addr + 0xD0C)

    def write_dhcsr(self, v):
        return self.ap.write_32(v, self.scb.addr + 0xDF0)

    def write_dcrsr(self, v):
        return self.ap.write_32(v, self.scb.addr + 0xDF4)

    def write_dcrdr(self, v):
        return self.ap.write_32(v, self.scb.addr + 0xDF8)

    def write_demcr(self, v):
        return self.ap.write_32(v, self.scb.addr + 0xDFC)

    def write_core_register(self, v, sel):
        '''Writes a single core register.'''
        assert self.flags & FLAG_HALTED
        assert sel < 128

        self.write_dcrdr(v)
        self.write_dcrsr((1<<16) | sel)
        while not (self.read_dhcsr() & (1<<16)):
            time.sleep(0.001)

    def halt(self):
        '''Halts the CPU.'''
        if self.flags & FLAG_HALTED:
            return

        self.write_dhcsr(0xA05F0000 | (1<<1) | (1<<0))
        while not (self.read_dhcsr() & (1<<17)):
            time.sleep(0.001)
        self.flags |= FLAG_HALTED

    def reset_halt(self):
        '''Resets the CPU and halts on the Reset exception.'''
        # Set DHCSR.C_DEBUGEN to enable Halting debug.
        self.halt()

        # Set DEMCR.VC_CORERESET to enable reset vector catch.
        self.write_demcr(0x01000001)

        # Set AIRCR.SYSRESETREQ and then wait for it to clear.  Accesses after
        # the AIRCR write can cause a DP fault on the ST-Link; catch and ignore
        # them.
        self.write_aircr((self.read_aircr() & 0x0000FFF8) | 0x05FA0004)
        while True:
            try:
                v = self.read_aircr()
                if not (v & 4):
                    break
                time.sleep(0.001)
            except:
                pass

        # Clear DEMCR.VC_CORESET so that future resets don't catch.
        self.write_demcr(0x01000000)

    def resume(self):
        '''Resumes execution of a halted CPU.'''
        if not (self.flags & FLAG_HALTED):
            return

        self.write_dhcsr(0xA05F0000)
        while self.read_dhcsr() & (1<<17):
            time.sleep(0.001)
        self.flags &= ~FLAG_HALTED
