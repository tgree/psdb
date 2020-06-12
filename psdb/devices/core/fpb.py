# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from psdb.devices import Reg32
from .cortex_subdevice import CortexSubDevice


class FPB(CortexSubDevice):
    '''
    Driver for Cortex V7-M (M4, M7) Flash Patch and Breakpoint unit.
    '''
    REGS = [Reg32('FP_CTRL',    0x00,  [('ENABLE',          1),
                                        ('KEY',             1),
                                        ('',                2),
                                        ('NUM_CODE[3:0]',   4),
                                        ('NUM_LIT',         4),
                                        ('NUM_CODE[6:4]',   3),
                                        ('',                13),
                                        ('REV',             4),
                                        ]),
            Reg32('FP_REMAP',   0x04,  [('',                5),
                                        ('REMAP',           24),
                                        ('RMPSPT',          1),
                                        ]),
            Reg32('FP_COMP0',   0x08),
            Reg32('FP_COMP1',   0x0C),
            Reg32('FP_COMP2',   0x10),
            Reg32('FP_COMP3',   0x14),
            Reg32('FP_COMP4',   0x18),
            Reg32('FP_COMP5',   0x1C),
            Reg32('FP_COMP6',   0x20),
            Reg32('FP_COMP7',   0x24),
            ]

    def __init__(self, component, subtype):
        super(FPB, self).__init__('FPB', FPB.REGS, component, subtype)
        fp_ctrl       = self._FP_CTRL.read()
        self.ncode    = (((fp_ctrl >> 4) & 0x0F) |
                         ((fp_ctrl >> 8) & 0xF0))
        self.nlit     = ((fp_ctrl >> 8) & 0x0F)
        self.revision = ((fp_ctrl >> 28) & 0x0F) + 1
        assert self.revision in (1, 2)

        self.free_breakpoints   = list(range(self.ncode))
        self.active_breakpoints = {}

    def __repr__(self):
        return (super(FPB, self).__repr__() +
                (' (rev %u: %u code breakpoints, %u literals)'
                 % (self.revision, self.ncode, self.nlit)))

    def _write_comp(self, v, index):
        self._write_32(v, 0x08 + 4*index)

    def _insert_breakpoint_rev1(self, addr):
        assert ((addr & 0xE0000001) == 0)
        index   = self.free_breakpoints.pop(0)
        replace = (1 if not (addr & 2) else 2)
        comp    = (addr & 0x1FFFFFFC)
        self._write_comp((replace << 30) | comp | 1, index)
        return index

    def _insert_breakpoint_rev2(self, addr):
        assert ((addr & 0x00000001) == 0)
        index  = self.free_breakpoints.pop(0)
        self._write_comp(addr | 1, index)
        return index

    def insert_breakpoint(self, addr):
        if addr in self.active_breakpoints:
            return

        if self.revision == 1:
            index = self._insert_breakpoint_rev1(addr)
        elif self.revision == 2:
            index = self._insert_breakpoint_rev2(addr)
        else:
            raise Exception('Unrecognized FPB revision %u' % self.revision)

        self.active_breakpoints[addr] = index
        if len(self.active_breakpoints) == 1:
            self._FP_CTRL = (1 << 1) | (1 << 0)

    def remove_breakpoint(self, addr):
        if addr not in self.active_breakpoints:
            return

        if self.revision in (1, 2):
            index = self.active_breakpoints[addr]
            self._write_comp(0x00000000, index)
        else:
            raise Exception('Unrecognized FPB revision %u' % self.revision)

        del self.active_breakpoints[addr]
        self.free_breakpoints.append(index)
        if len(self.active_breakpoints) == 0:
            self._FP_CTRL = (1 << 1)

    def reset(self):
        self._FP_CTRL = (1 << 1)
        for i in range(self.ncode + self.nlit):
            self._write_comp(0x00000000, i)
