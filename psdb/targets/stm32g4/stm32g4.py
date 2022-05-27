# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb
from psdb.devices import MemDevice, RAMDevice, stm32, stm32g4
from psdb.targets import Target
from . import dbgmcu


DEVICES_2 = [(RAMDevice,       'CCM SRAM ID', 0x10000000, 0x00002800),
             (MemDevice,       'System ROM',  0x1FFF0000, 0x00007000),
             (RAMDevice,       'SRAM1',       0x20000000, 0x00004000),
             (RAMDevice,       'SRAM2',       0x20004000, 0x00001800),
             (RAMDevice,       'CCM SRAM S',  0x20005800, 0x00002800),
             (stm32.GPT32,     'TIM2',        0x40000000),
             (stm32.GPT16x4,   'TIM3',        0x40000400),
             (stm32.GPT16x4,   'TIM4',        0x40000800),
             (stm32.BT,        'TIM6',        0x40001000),
             (stm32.BT,        'TIM7',        0x40001400),
             (stm32g4.TAMP,    'TAMP',        0x40002400),
             (stm32g4.RTC,     'RTC',         0x40002800),
             (stm32g4.PWR,     'PWR',         0x40007000),
             (stm32.LPUART,    'LPUART1',     0x40008000),
             (stm32g4.SYSCFG,  'SYSCFG',      0x40010000),
             (stm32.VREF,      'VREF',        0x40010030),
             (stm32g4.COMP,    'COMP',        0x40010200),
             (stm32g4.OPAMP,   'OPAMP',       0x40010300),
             (stm32.ACT,       'TIM1',        0x40012C00),
             (stm32.ACT,       'TIM8',        0x40013400),
             (stm32.GPT16x2,   'TIM15',       0x40014000),
             (stm32.GPT16x1,   'TIM16',       0x40014400),
             (stm32.GPT16x1,   'TIM17',       0x40014800),
             (stm32.DMA,       'DMA1',        0x40020000),
             (stm32.DMA,       'DMA2',        0x40020400),
             (stm32.DMAMUX,    'DMAMUX',      0x40020800, 16, 4),
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
             (stm32.DAC_Saw,   'DAC1',        0x50000800),
             (stm32.DAC_Saw,   'DAC3',        0x50001000),
             (stm32g4.DBGMCU,  'DBGMCU',      0xE0042000),
             ]

DEVICES_3 = [(RAMDevice,       'CCM SRAM ID', 0x10000000, 0x00008000),
             (MemDevice,       'System ROM',  0x1FFF0000, 0x00007000),
             (RAMDevice,       'SRAM1',       0x20000000, 0x00014000),
             (RAMDevice,       'SRAM2',       0x20014000, 0x00004000),
             (RAMDevice,       'CCM SRAM S',  0x20018000, 0x00008000),
             (stm32.GPT32,     'TIM2',        0x40000000),
             (stm32.GPT16x4,   'TIM3',        0x40000400),
             (stm32.GPT16x4,   'TIM4',        0x40000800),
             (stm32.GPT32,     'TIM5',        0x40000C00),
             (stm32.BT,        'TIM6',        0x40001000),
             (stm32.BT,        'TIM7',        0x40001400),
             (stm32g4.TAMP,    'TAMP',        0x40002400),
             (stm32g4.RTC,     'RTC',         0x40002800),
             (stm32g4.PWR,     'PWR',         0x40007000),
             (stm32.LPUART,    'LPUART1',     0x40008000),
             (stm32g4.SYSCFG,  'SYSCFG',      0x40010000),
             (stm32.VREF,      'VREF',        0x40010030),
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
             (stm32.DMAMUX,    'DMAMUX',      0x40020800, 16, 4),
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
             (stm32.DAC_Saw,   'DAC1',        0x50000800),
             (stm32.DAC_Saw,   'DAC2',        0x50000C00),
             (stm32.DAC_Saw,   'DAC3',        0x50001000),
             (stm32.DAC_Saw,   'DAC4',        0x50001400),
             (stm32.QUADSPI,   'QUADSPI',     0xA0001000),
             (stm32g4.DBGMCU,  'DBGMCU',      0xE0042000),
             ]


DEVICES_4 = [(RAMDevice,       'CCM SRAM ID', 0x10000000, 0x00004000),
             (MemDevice,       'System ROM',  0x1FFF0000, 0x00007000),
             (RAMDevice,       'SRAM1',       0x20000000, 0x00014000),
             (RAMDevice,       'SRAM2',       0x20014000, 0x00004000),
             (RAMDevice,       'CCM SRAM S',  0x20018000, 0x00004000),
             (stm32.GPT32,     'TIM2',        0x40000000),
             (stm32.GPT16x4,   'TIM3',        0x40000400),
             (stm32.GPT16x4,   'TIM4',        0x40000800),
             (stm32.BT,        'TIM6',        0x40001000),
             (stm32.BT,        'TIM7',        0x40001400),
             (stm32g4.TAMP,    'TAMP',        0x40002400),
             (stm32g4.RTC,     'RTC',         0x40002800),
             (stm32g4.PWR,     'PWR',         0x40007000),
             (stm32.LPUART,    'LPUART1',     0x40008000),
             (stm32g4.SYSCFG,  'SYSCFG',      0x40010000),
             (stm32.VREF,      'VREF',        0x40010030),
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
             (stm32.DMAMUX,    'DMAMUX',      0x40020800, 16, 4),
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
             (stm32.DAC_Saw,   'DAC1',        0x50000800),
             (stm32.DAC_Saw,   'DAC3',        0x50001000),
             (stm32.QUADSPI,   'QUADSPI',     0xA0001000),
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

        self.orig_fb_mode = self._get_fb_mode()
        self.fb_mode      = self._synchronize_fb_mode()

    def __repr__(self):
        return 'STM32G4 MCU_IDCODE 0x%08X' % self.mcu_idcode

    def halt(self):
        super().halt()
        self._set_fb_mode(self.fb_mode)

    def reset_halt(self):
        super().reset_halt()
        self.orig_fb_mode = self._get_fb_mode()
        self.fb_mode      = self._synchronize_fb_mode()

    def resume(self):
        self._set_fb_mode(self.orig_fb_mode)
        super().resume()

    def _set_fb_mode(self, v):
        rcc                    = self.devs['RCC']
        syscfg                 = self.devs['SYSCFG']
        syscfgen               = rcc._APB2ENR.SYSCFGEN
        rcc._APB2ENR.SYSCFGEN  = 1
        syscfg._MEMRMP.FB_MODE = v
        rcc._APB2ENR.SYSCFGEN  = syscfgen

    def _get_fb_mode(self):
        rcc                    = self.devs['RCC']
        syscfg                 = self.devs['SYSCFG']
        syscfgen               = rcc._APB2ENR.SYSCFGEN
        rcc._APB2ENR.SYSCFGEN  = 1
        fb_mode                = syscfg._MEMRMP.FB_MODE
        rcc._APB2ENR.SYSCFGEN  = syscfgen
        return fb_mode

    def _synchronize_fb_mode(self):
        '''
        Ensure FB_MODE matches BFB2 (not the case when we halt out of reset
        with BFB2=1).  This is critical for just about anything that touches
        flash.
        '''
        bfb2 = self.flash.get_options()['bfb2']
        self._set_fb_mode(bfb2)
        return bfb2

    def enable_rtc(self, rtcsel=1):
        rcc = self.devs['RCC']
        pwr = self.devs['PWR']
        rtc = self.devs['RTC']
        rcc.enable_device('PWR')
        pwr.unlock_backup_domain()
        rcc.set_lse_drive_capability(0)
        rcc.enable_lse()
        rcc.set_rtcclock_source(rtcsel)
        rcc.enable_rtc()
        rtc.init()

    @staticmethod
    def is_mcu(db):
        # Only APSEL 0 should be populated.
        if set(db.aps) != set((0,)):
            return False

        # APSEL 0 should be an AHB3 AP.
        ap = db.aps[0]
        if not isinstance(ap, psdb.access_port.AHB3AP):
            return False

        # Identify the STM32G4 through the base component's CIDR/PIDR
        # registers.
        c = db.aps[0].base_component
        if not c:
            c = db.aps[0].probe_components(match=False, recurse=False)
        if not c:
            return False
        if c.cidr != 0xB105100D:
            return False
        if c.pidr not in (0xA0468, 0xA0469, 0xA0479):
            return False

        # Finally, we can match on the DBGMCU IDC value.
        if dbgmcu.read_idc_dev_id(db) not in (0x468, 0x469, 0x479):
            return False

        return True

    @staticmethod
    def pre_probe(db, verbose):
        # Ensure this is an STM32G4 part.
        if not STM32G4.is_mcu(db):
            return

        # Enable all the clocks we want to use.
        cr = dbgmcu.read_cr(db)
        if (cr & 0x00000007) != 0x00000007:
            if verbose:
                print('Detected STM32G4, enabling all DBGMCU debug clocks.')
            dbgmcu.write_cr(db, cr | 0x00000007)

    @staticmethod
    def probe(db):
        # Ensure this is an STM32G4 part.
        if not STM32G4.is_mcu(db):
            return None

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        return STM32G4(db)
