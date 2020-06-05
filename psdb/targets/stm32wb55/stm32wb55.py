# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import psdb
from .flash import FLASH
from .sram import SRAM
from .pwr import PWR
from .rcc import RCC
from .ipcc import IPCC
from ..stm32g4.general_purpose_timer_32 import GPT32
from ..stm32g4.gpio import GPIO
from ..stm32g4.adc import ADC
from ..stm32g4.dma import DMA
from ..stm32g4.dma_mux import DMAMUX
from ..stm32 import USB
from ..device import MemDevice
from .ipc import IPC
from psdb.targets import Target


DEVICES = [(SRAM,   'SRAM1',    0x20000000, 0x00030000),
           (SRAM,   'SRAM2a',   0x20030000, 0x00008000),
           (SRAM,   'SRAM2b',   0x20038000, 0x00008000),
           (GPT32,  'TIM2',     0x40000000),
           (USB,    'USB',      0x40006800),
           (DMA,    'DMA1',     0x40020000),
           (DMA,    'DMA2',     0x40020400),
           (DMAMUX, 'DMAMUX',   0x40020800),
           (GPIO,   'GPIOA',    0x48000000),
           (GPIO,   'GPIOB',    0x48000400),
           (GPIO,   'GPIOC',    0x48000800),
           (GPIO,   'GPIOD',    0x48000C00),
           (GPIO,   'GPIOE',    0x48001000),
           (GPIO,   'GPIOH',    0x48001C00),
           (ADC,    'ADC1',     0x50040000, 1, 1),
           (RCC,    'RCC',      0x58000000),
           (PWR,    'PWR',      0x58000400),
           (IPCC,   'IPCC',     0x58000C00),
           (FLASH,  'FLASH',    0x58004000, 0x08000000, 3300000,
                                0x1FFF7000, 1024),
           ]


class STM32WB55(Target):
    def __init__(self, db):
        super(STM32WB55, self).__init__(db, 24000000)
        self.ahb_ap     = self.db.aps[0]
        self.uuid       = self.ahb_ap.read_bulk(0x1FFF7590, 12)
        self.flash_size = (self.ahb_ap.read_32(0x1FFF75E0) & 0x0000FFFF)*1024
        self.package    = self.ahb_ap.read_32(0x1FFF7500) & 0x0000001F
        self.mcu_idcode = self.ahb_ap.read_32(0xE0042000)

        for d in DEVICES:
            cls  = d[0]
            name = d[1]
            addr = d[2]
            args = d[3:]
            cls(self, self.ahb_ap, name, addr, *args)

        self.flash = self.devs['FLASH']
        MemDevice(self, self.ahb_ap, 'FBANKS', self.flash.mem_base,
                  self.flash.user_flash_size)
        MemDevice(self, self.ahb_ap, 'OTP', self.flash.otp_base,
                  self.flash.otp_len)
        self.devs['SRAM2a'].size = self.flash.user_sram2a_size
        self.devs['SRAM2b'].size = self.flash.user_sram2b_size

        ipccdba = self.flash.get_ipccdba()
        sram1   = self.devs['SRAM1']
        sram2a  = self.devs['SRAM2a']
        size    = sram2a.size - (ipccdba - sram2a.dev_base)
        self.ipc = IPC(self, self.ahb_ap, ipccdba, size, sram1.dev_base)

    def __repr__(self):
        return 'STM32WB55 MCU_IDCODE 0x%08X' % self.mcu_idcode

    def configure_rf_clocks(self):
        '''
        Configures all clock subsystems as required for the BLE firmware to be
        able to boot up and start handling commands.
        '''
        rcc = self.devs['RCC']
        pwr = self.devs['PWR']

        # Tune the 32 MHz oscillator.
        rcc.apply_hse_tuning()

        # Enable access to the backup domain.
        pwr.enable_backup_domain()

        # Reset the backup domain.
        rcc.reset_backup_domain()

        # Enable the LSE drive capability.
        rcc.set_lse_drive_capability(0)

        # Set voltage range 1 (up to 64 MHz).
        pwr.set_voltage_scaling(1)

        # Enable oscillators.
        rcc.enable_hse()
        rcc.enable_hsi()
        rcc.enable_lse()

        # Configure all clock prescalers.
        self.flash.set_wait_states(1)
        rcc.set_hpre(1)
        rcc.set_c2hpre(1)
        rcc.set_shdhpre(1)
        rcc.set_ppre1(1)
        rcc.set_ppre2(1)

        # Select SYSCLOCK = HSE.
        rcc.set_sysclock_source(2)

        # Select other clock sources:
        #   RTCCLOCK      = LSE
        #   USART1CLOCK   = PCLK
        #   LPUARTCLOCK   = PCLK
        #   RFWAKEUPCLOCK = LSE
        #   SMPSCLOCK     = HSE
        #   SMPSDIV       = RANGE1
        rcc.set_rtcclock_source(1)
        rcc.set_usart1clock_source(0)
        rcc.set_lpuartclock_source(0)
        rcc.set_rfwakeupclock_source(1)
        rcc.set_smps_div(1)
        rcc.set_smpsclock_source(2)

    @staticmethod
    def probe(db):
        # APSEL 0 and 1 should be populated and be AHB APs.
        for i in range(2):
            if i not in db.aps:
                return None

            ap = db.aps[i]
            if not isinstance(ap, psdb.access_port.AHBAP):
                return None
        
        # Identify the STM32WB55 through the base component's CIDR/PIDR
        # registers.
        c = db.aps[0].base_component
        if not c or c.cidr != 0xB105100D or c.pidr != 0x00000000000A0495:
            return None

        # While the STM32WB55 has two CPUs, the second one is inaccessible due
        # to ST security.
        if len(db.cpus) != 1:
            return None

        return STM32WB55(db)
