# Copyright (c) 2023 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32


class GPDMA(Device):
    '''
    Driver for the STM32U5 GPDMA (General-Purpose DMA).
    '''
    REGS = [AReg32('SECCFGR',   0x00),
            AReg32('PRIVCFGR',  0x04),
            AReg32('RCFGLOCKR', 0x08),
            AReg32('MISR',      0x0C),
            AReg32('SMISR',     0x10),
            AReg32('C0LBAR',    0x50),
            AReg32('C0FCR',     0x5C),
            AReg32('C0SR',      0x60),
            AReg32('C0CR',      0x64),
            AReg32('C0TR1',     0x90),
            AReg32('C0TR2',     0x94),
            AReg32('C0BR1',     0x98),
            AReg32('C0SAR',     0x9C),
            AReg32('C0DAR',     0xA0),
            AReg32('C0TR3',     0xA4),
            AReg32('C0BR2',     0xA8),
            AReg32('C0LLR',     0xCC),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, GPDMA.REGS, **kwargs)
