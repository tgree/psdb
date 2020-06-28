# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb
from psdb.devices import MemDevice, stm32, stm32g4
from psdb.targets import Target


DEVICES_2 = [(MemDevice,       'CCM SRAM ID', 0x10000000, 0x00002800),
             (MemDevice,       'SRAM1',       0x20000000, 0x00004000),
             (MemDevice,       'SRAM2',       0x20004000, 0x00001800),
             (MemDevice,       'CCM SRAM S',  0x20005800, 0x00002800),
             (stm32.GPT32,     'TIM2',        0x40000000),
             (stm32.GPT16x4,   'TIM3',        0x40000400),
             (stm32.GPT16x4,   'TIM4',        0x40000800),
             (stm32.BT,        'TIM6',        0x40001000),
             (stm32.BT,        'TIM7',        0x40001400),
             (stm32g4.PWR,     'PWR',         0x40007000),
             (stm32g4.SYSCFG,  'SYSCFG',      0x40010000),
             (stm32g4.VREF,    'VREF',        0x40010030),
             (stm32g4.COMP,    'COMP',        0x40010200),
             (stm32g4.OPAMP,   'OPAMP',       0x40010300),
             (stm32.ACT,       'TIM1',        0x40012C00),
             (stm32.ACT,       'TIM8',        0x40013400),
             (stm32.GPT16x2,   'TIM15',       0x40014000),
             (stm32.GPT16x1,   'TIM16',       0x40014400),
             (stm32.GPT16x1,   'TIM17',       0x40014800),
             (stm32.DMA,       'DMA1',        0x40020000),
             (stm32.DMA,       'DMA2',        0x40020400),
             (stm32.DMAMUX,    'DMAMUX',      0x40020800),
             (stm32g4.RCC,     'RCC',         0x40021000),
             (stm32g4.FLASH_2, 'FLASH',       0x40022000, 0x08000000, 3300000,
                                              0x1FFF7000, 1024),  # noqa: E127
             (stm32.GPIO,      'GPIOA',       0x48000000),
             (stm32.GPIO,      'GPIOB',       0x48000400),
             (stm32.GPIO,      'GPIOC',       0x48000800),
             (stm32.GPIO,      'GPIOD',       0x48000C00),
             (stm32.GPIO,      'GPIOE',       0x48001000),
             (stm32.GPIO,      'GPIOF',       0x48001400),
             (stm32.GPIO,      'GPIOG',       0x48001800),
             (stm32.ADC,       'ADC12',       0x50000000, 1, 2),
             (stm32.DAC,       'DAC1',        0x50000800),
             (stm32.DAC,       'DAC3',        0x50001000),
             (stm32g4.DBGMCU,  'DBGMCU',      0xE0042000),
             ]

DEVICES_3 = [(MemDevice,       'CCM SRAM ID', 0x10000000, 0x00008000),
             (MemDevice,       'SRAM1',       0x20000000, 0x00014000),
             (MemDevice,       'SRAM2',       0x20014000, 0x00004000),
             (MemDevice,       'CCM SRAM S',  0x20018000, 0x00008000),
             (stm32.GPT32,     'TIM2',        0x40000000),
             (stm32.GPT16x4,   'TIM3',        0x40000400),
             (stm32.GPT16x4,   'TIM4',        0x40000800),
             (stm32.GPT32,     'TIM5',        0x40000C00),
             (stm32.BT,        'TIM6',        0x40001000),
             (stm32.BT,        'TIM7',        0x40001400),
             (stm32g4.PWR,     'PWR',         0x40007000),
             (stm32g4.SYSCFG,  'SYSCFG',      0x40010000),
             (stm32g4.VREF,    'VREF',        0x40010030),
             (stm32g4.COMP,    'COMP',        0x40010200),
             (stm32g4.OPAMP,   'OPAMP',       0x40010300),
             (stm32.ACT,       'TIM1',        0x40012C00),
             (stm32.ACT,       'TIM8',        0x40013400),
             (stm32.GPT16x2,   'TIM15',       0x40014000),
             (stm32.GPT16x1,   'TIM16',       0x40014400),
             (stm32.GPT16x1,   'TIM17',       0x40014800),
             (stm32.ACT,       'TIM20',       0x40015000),
             (stm32.DMA,       'DMA1',        0x40020000),
             (stm32.DMA,       'DMA2',        0x40020400),
             (stm32.DMAMUX,    'DMAMUX',      0x40020800),
             (stm32g4.RCC,     'RCC',         0x40021000),
             (stm32g4.FLASH_3, 'FLASH',       0x40022000, 0x08000000, 3300000,
                                              0x1FFF7000, 1024),  # noqa: E127
             (stm32.GPIO,      'GPIOA',       0x48000000),
             (stm32.GPIO,      'GPIOB',       0x48000400),
             (stm32.GPIO,      'GPIOC',       0x48000800),
             (stm32.GPIO,      'GPIOD',       0x48000C00),
             (stm32.GPIO,      'GPIOE',       0x48001000),
             (stm32.GPIO,      'GPIOF',       0x48001400),
             (stm32.GPIO,      'GPIOG',       0x48001800),
             (stm32.ADC,       'ADC12',       0x50000000, 1, 2),
             (stm32.ADC,       'ADC345',      0x50000400, 3, 3),
             (stm32.DAC,       'DAC1',        0x50000800),
             (stm32.DAC,       'DAC2',        0x50000C00),
             (stm32.DAC,       'DAC3',        0x50001000),
             (stm32.DAC,       'DAC4',        0x50001400),
             (stm32g4.DBGMCU,  'DBGMCU',      0xE0042000),
             ]


DEVICES_4 = [(MemDevice,       'CCM SRAM ID', 0x10000000, 0x00004000),
             (MemDevice,       'SRAM1',       0x20000000, 0x00014000),
             (MemDevice,       'SRAM2',       0x20014000, 0x00004000),
             (MemDevice,       'CCM SRAM S',  0x20018000, 0x00004000),
             (stm32.GPT32,     'TIM2',        0x40000000),
             (stm32.GPT16x4,   'TIM3',        0x40000400),
             (stm32.GPT16x4,   'TIM4',        0x40000800),
             (stm32.BT,        'TIM6',        0x40001000),
             (stm32.BT,        'TIM7',        0x40001400),
             (stm32g4.PWR,     'PWR',         0x40007000),
             (stm32g4.SYSCFG,  'SYSCFG',      0x40010000),
             (stm32g4.VREF,    'VREF',        0x40010030),
             (stm32g4.COMP,    'COMP',        0x40010200),
             (stm32g4.OPAMP,   'OPAMP',       0x40010300),
             (stm32.ACT,       'TIM1',        0x40012C00),
             (stm32.ACT,       'TIM8',        0x40013400),
             (stm32.GPT16x2,   'TIM15',       0x40014000),
             (stm32.GPT16x1,   'TIM16',       0x40014400),
             (stm32.GPT16x1,   'TIM17',       0x40014800),
             (stm32.ACT,       'TIM20',       0x40015000),
             (stm32.DMA,       'DMA1',        0x40020000),
             (stm32.DMA,       'DMA2',        0x40020400),
             (stm32.DMAMUX,    'DMAMUX',      0x40020800),
             (stm32g4.RCC,     'RCC',         0x40021000),
             (stm32g4.FLASH_4, 'FLASH',       0x40022000, 0x08000000, 3300000,
                                              0x1FFF7000, 1024),  # noqa: E127
             (stm32.GPIO,      'GPIOA',       0x48000000),
             (stm32.GPIO,      'GPIOB',       0x48000400),
             (stm32.GPIO,      'GPIOC',       0x48000800),
             (stm32.GPIO,      'GPIOD',       0x48000C00),
             (stm32.GPIO,      'GPIOE',       0x48001000),
             (stm32.GPIO,      'GPIOF',       0x48001400),
             (stm32.GPIO,      'GPIOG',       0x48001800),
             (stm32.ADC,       'ADC12',       0x50000000, 1, 2),
             (stm32.ADC,       'ADC3',        0x50000400, 3, 1),
             (stm32.DAC,       'DAC1',        0x50000800),
             (stm32.DAC,       'DAC3',        0x50001000),
             (stm32g4.DBGMCU,  'DBGMCU',      0xE0042000),
             ]


class STM32G4(Target):
    def __init__(self, db):
        super(STM32G4, self).__init__(db, 24000000)
        self.ahb_ap     = self.db.aps[0]
        self.uuid       = self.ahb_ap.read_bulk(0x1FFF7590, 12)
        self.flash_size = (self.ahb_ap.read_32(0x1FFF75E0) & 0x0000FFFF)*1024
        self.package    = self.ahb_ap.read_32(0x1FFF7500) & 0x0000001F
        self.mcu_idcode = self.ahb_ap.read_32(0xE0042000)

        dev_id = (self.mcu_idcode & 0x0FFF)
        if dev_id == 0x468:
            DEVICES = DEVICES_2
        elif dev_id == 0x469:
            DEVICES = DEVICES_3
        elif dev_id == 0x479:
            DEVICES = DEVICES_4
        else:
            raise Exception('Unrecognized category MCU_IDCODE 0x%08X' %
                            self.mcu_idcode)

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
        if (not c or c.cidr != 0xB105100D or
                c.pidr not in (0xA0468, 0xA0469, 0xA0479)):
            return None

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        return STM32G4(db)
