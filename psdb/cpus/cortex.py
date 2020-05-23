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
    ('msp',  17),
    ('psp',  18),
    ('cfbp', 20),
])


class Cortex(psdb.component.Component):
    '''
    Base class component matcher for Cortex CPUs.  This is where we have common
    code for Cortex-M4 and Cortex-M7; there's no guarantee that this will work
    for any other Cortex model.
    '''
    def __init__(self, component, subtype):
        super(Cortex, self).__init__(component.parent, component.ap,
                                     component.addr, subtype)
        self.scs       = None
        self.flags     = 0
        self.cpu_index = len(self.ap.db.cpus)
        self.ap.db.cpus.append(self)

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

    def _read_core_register(self, sel):
        assert self.flags & FLAG_HALTED
        assert sel < 128

        self.scs._DCRSR = sel
        while not self.scs._DHCSR.S_REGRDY:
            time.sleep(0.001)
        return self.scs._DCRDR.read()

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

    def write_demcr(self, v):
        return self.ap.write_32(v, self.scs.addr + 0xDFC)

    def write_core_register(self, v, sel):
        '''Writes a single core register.'''
        assert self.flags & FLAG_HALTED
        assert sel < 128

        self.scs._DCRDR = v
        self.scs._DCRSR = ((1<<16) | sel)
        while not self.scs._DHCSR.S_REGRDY:
            time.sleep(0.001)

    def halt(self):
        '''Halts the CPU.'''
        if self.flags & FLAG_HALTED:
            return

        self.scs._DHCSR = (0xA05F0000 | (1<<1) | (1<<0))
        while not self.scs._DHCSR.S_HALT:
            time.sleep(0.001)
        self.flags |= FLAG_HALTED

    def reset_halt(self):
        '''Resets the CPU and halts on the Reset exception.'''
        # Set DHCSR.C_DEBUGEN to enable Halting debug.
        self.halt()

        # Set DEMCR.VC_CORERESET to enable reset vector catch.
        self.scs._DEMCR.VC_CORERESET = 1

        # Set AIRCR.SYSRESETREQ and then wait for it to clear.  Accesses after
        # the AIRCR write can cause a DP fault on the ST-Link; catch and ignore
        # them.
        self.scs._AIRCR((self.scs._AIRCR.read() & 0x0000FFF8) | 0x05FA0004)
        while True:
            try:
                if not self.scs._AIRCR.SYSRESETREQ:
                    break
                time.sleep(0.001)
            except Exception:
                pass

        # Clear DEMCR.VC_CORESET so that future resets don't catch.
        self.write_demcr(0x01000000)

    def resume(self):
        '''Resumes execution of a halted CPU.'''
        if not (self.flags & FLAG_HALTED):
            return

        self.scs._DHCSR = 0xA05F0000
        while self.scs._DHCSR.S_HALT:
            time.sleep(0.001)
        self.flags &= ~FLAG_HALTED
