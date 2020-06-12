# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from psdb.devices import Reg32
from .cortex_subdevice import CortexSubDevice


class BPU(CortexSubDevice):
    '''
    Driver for Cortex V6-M (M0+) Breakpoint Unit.
    '''
    REGS = [Reg32('BP_CTRL',    0x00,  [('ENABLE',      1),
                                        ('KEY',         1),
                                        ('',            2),
                                        ('NUM_CODE',    4),
                                        ]),
            Reg32('BP_COMP0',   0x08),
            Reg32('BP_COMP1',   0x0C),
            Reg32('BP_COMP2',   0x10),
            Reg32('BP_COMP3',   0x14),
            ]

    def __init__(self, component, subtype):
        super(BPU, self).__init__('BPU', BPU.REGS, component, subtype)
        bp_ctrl       = self._BP_CTRL.read()
        self.ncode    = ((bp_ctrl >> 4) & 0x0F)

        self.free_breakpoints   = list(range(self.ncode))
        self.active_breakpoints = {}

    def __repr__(self):
        return super(BPU, self).__repr__() + (' (%u breakpoints)' % self.ncode)

    def _write_comp(self, v, index):
        self._write_32(v, 0x08 + 4*index)

    def insert_breakpoint(self, addr):
        if addr in self.active_breakpoints:
            return

        assert ((addr & 0xE0000001) == 0)
        index    = self.free_breakpoints.pop(0)
        bp_match = (1 if not (addr & 2) else 2)
        comp     = (addr & 0x1FFFFFFC)
        self._write_comp((bp_match << 30) | comp | 1, index)

        self.active_breakpoints[addr] = index
        if len(self.active_breakpoints) == 1:
            self._BP_CTRL = (1 << 1) | (1 << 0)

    def remove_breakpoint(self, addr):
        if addr not in self.active_breakpoints:
            return

        index = self.active_breakpoints[addr]
        self._write_comp(0x00000000, index)

        del self.active_breakpoints[addr]
        self.free_breakpoints.append(index)
        if len(self.active_breakpoints) == 0:
            self._BP_CTRL = (1 << 1)

    def reset(self):
        self._BP_CTRL = (1 << 1)
        for i in range(self.ncode):
            self._write_comp(0x00000000, i)
