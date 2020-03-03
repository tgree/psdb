# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb
from .flash import FLASH
from .sram import SRAM
from .pwr import PWR
from .rcc import RCC
from .vrefbuf import VREF
from .gpio import GPIO
from .dma import DMA
from .dma_mux import DMAMUX
from .general_purpose_timer_16x1 import GPT16x1
from .general_purpose_timer_16x2 import GPT16x2
from .general_purpose_timer_16x4 import GPT16x4
from .general_purpose_timer_32 import GPT32
from .advanced_control_timer import ACT
from .basic_timer import BT
from .adc import ADC
from .dac import DAC
from .comparator import COMP
from .opamp import OPAMP
from ..device import MemDevice
from psdb.targets import Target


DEVICES = [(SRAM,    'CCM SRAM', 0x20018000, 0x00008000),
           (SRAM,    'SRAM1',    0x20000000, 0x00014000),
           (SRAM,    'SRAM2',    0x20014000, 0x00004000),
           (GPT32,   'TIM2',     0x40000000),
           (GPT16x4, 'TIM3',     0x40000400),
           (GPT16x4, 'TIM4',     0x40000800),
           (GPT32,   'TIM5',     0x40000C00),
           (BT,      'TIM6',     0x40001000),
           (BT,      'TIM7',     0x40001400),
           (PWR,     'PWR',      0x40007000),
           (VREF,    'VREF',     0x40010030),
           (COMP,    'COMP1',    0x40010200),
           (OPAMP,   'OPAMP',    0x40010300),
           (ACT,     'TIM1',     0x40012C00),
           (ACT,     'TIM8',     0x40013400),
           (GPT16x2, 'TIM15',    0x40014000),
           (GPT16x1, 'TIM16',    0x40014400),
           (GPT16x1, 'TIM17',    0x40014800),
           (ACT,     'TIM20',    0x40015000),
           (DMA,     'DMA1',     0x40020000),
           (DMA,     'DMA2',     0x40020400),
           (DMAMUX,  'DMAMUX',   0x40020800),
           (RCC,     'RCC',      0x40021000),
           (FLASH,   'FLASH',    0x40022000, 0x08000000, 3300000,
                                 0x1FFF7000, 1024),
           (GPIO,    'GPIOA',    0x48000000),
           (GPIO,    'GPIOB',    0x48000400),
           (GPIO,    'GPIOC',    0x48000800),
           (GPIO,    'GPIOD',    0x48000C00),
           (GPIO,    'GPIOE',    0x48001000),
           (GPIO,    'GPIOF',    0x48001400),
           (GPIO,    'GPIOG',    0x48001800),
           (ADC,     'ADC12',    0x50000000, 1, 2),
           (ADC,     'ADC345',   0x50000400, 3, 3),
           (DAC,     'DAC1',     0x50000800),
           (DAC,     'DAC2',     0x50000C00),
           (DAC,     'DAC3',     0x50001000),
           (DAC,     'DAC4',     0x50001400),
           ]


class STM32G4(Target):
    def __init__(self, db):
        super(STM32G4, self).__init__(db, 24000000)
        self.ahb_ap     = self.db.aps[0]
        self.uuid       = self.ahb_ap.read_bulk(0x1FFF7590, 12)
        self.flash_size = (self.ahb_ap.read_32(0x1FFF75E0) & 0x0000FFFF)*1024
        self.mcu_idcode = self.ahb_ap.read_32(0xE0042000)

        for d in DEVICES:
            cls  = d[0]
            name = d[1]
            addr = d[2]
            args = d[3:]
            cls(self, self.ahb_ap, name, addr, *args)

        self.flash = self.devs['FLASH']
        MemDevice(self, self.ahb_ap, 'FBANKS', self.flash.mem_base,
                  self.flash.flash_size)
        MemDevice(self, self.ahb_ap, 'OTP', self.flash.otp_base,
                  self.flash.otp_len)

    def __repr__(self):
        return 'STM32G4 MCU_IDCODE 0x%08X' % self.mcu_idcode

    @staticmethod
    def probe(db):
        # APSEL 0 should be populated.
        if 0 not in db.aps:
            return None

        # APSEL 0 should be an AHB AP.
        ap = db.aps[0]
        if not isinstance(ap, psdb.access_port.AHBAP):
            return None

        # Identify the STM32G4 through the base component's CIDR/PIDR
        # registers.
        c = db.aps[0].base_component
        if not c or c.cidr != 0xB105100D or c.pidr != 0x00000000000A0469:
            return None

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        return STM32G4(db)
