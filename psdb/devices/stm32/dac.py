# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class DAC(Device):
    '''
    Driver for the STM32 DAC.
    '''
    REGS = [Reg32('CR',      0x000),
            Reg32('SWTRGR',  0x004),
            Reg32('DHR12R1', 0x008),
            Reg32('DHR12L1', 0x00C),
            Reg32('DHR8R1',  0x010),
            Reg32('DHR12R2', 0x014),
            Reg32('DHR12L2', 0x018),
            Reg32('DHR8R2',  0x01C),
            Reg32('DHR12RD', 0x020),
            Reg32('DHR12LD', 0x024),
            Reg32('DHR8RD',  0x028),
            Reg32('DOR1',    0x02C),
            Reg32('DOR2',    0x030),
            Reg32('SR',      0x034),
            Reg32('CCR',     0x038),
            Reg32('MCR',     0x03C),
            Reg32('SHSR1',   0x040),
            Reg32('SHSR2',   0x044),
            Reg32('SHHR',    0x048),
            Reg32('SHRR',    0x04C),
            ]

    def __init__(self, target, ap, name, addr, sub_regs=None, **kwargs):
        regs = DAC.REGS + (sub_regs or [])
        super(DAC, self).__init__(target, ap, addr, name, regs, **kwargs)


class DAC_Saw(Device):
    '''
    Driver for DACs that have sawtooth functionality (STM32G4).

    The STM32G4 DAC can also take two values at once for a single channel,
    halving the number of DMA accesses required to generate a signal.
    '''
    STREGS = [Reg32('STR1',    0x058),
              Reg32('STR2',    0x05C),
              Reg32('STMODR',  0x060),
              ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(DAC_Saw, self).__init__(target, ap, name, addr,
                                      sub_regs=DAC_Saw.STREGS, **kwargs)
