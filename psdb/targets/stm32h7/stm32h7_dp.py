# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import time

import psdb
from psdb.devices import MemDevice, RAMDevice, stm32, stm32h7
from psdb.targets import Target
from . import dbgmcu


# AP0 devices are ones that we access via the M7 core.
AP0DEVS = [(RAMDevice,          'M7 ITCM',      0x00000000, 0x00010000),
           (RAMDevice,          'SRAM1 ID M7',  0x10000000, 0x00020000),
           (RAMDevice,          'SRAM2 ID M7',  0x10020000, 0x00020000),
           (RAMDevice,          'SRAM3 ID M7',  0x10040000, 0x00008000),
           (MemDevice,          'System ROM 1', 0x1FF00000, 0x00020000),
           (MemDevice,          'System ROM 2', 0x1FF40000, 0x00020000),
           (RAMDevice,          'M7 DTCM',      0x20000000, 0x00020000),
           (RAMDevice,          'AXI SRAM M7',  0x24000000, 0x00080000),
           (RAMDevice,          'SRAM1 M7',     0x30000000, 0x00020000),
           (RAMDevice,          'SRAM2 M7',     0x30020000, 0x00020000),
           (RAMDevice,          'SRAM3 M7',     0x30040000, 0x00008000),
           (stm32h7.TIM2_5,     'TIM2',         0x40000000),
           (stm32h7.TIM2_5,     'TIM5',         0x40000C00),
           (stm32h7.TIM6,       'TIM6',         0x40001000),
           (stm32h7.TIM7,       'TIM7',         0x40001400),
           (stm32.DAC,          'DAC1',         0x40007400),
           (stm32.CRS,          'CRS',          0x40008400),
           (stm32h7.OPAMP,      'OPAMP',        0x40009000),
           (stm32h7.TIM15,      'TIM15',        0x40014000),
           (stm32h7.TIM17,      'TIM17',        0x40014800),
           (stm32.DMA_DBM,      'DMA1',         0x40020000),
           (stm32.DMA_DBM,      'DMA2',         0x40020400),
           (stm32.DMAMUX,       'DMAMUX1',      0x40020800, 16, 8),
           (stm32.ADC16,        'ADC12',        0x40022000, 1, 2),
           (stm32h7.FLASH_DP,   'FLASH',        0x52002000, 0x08000000,
                                                8000000),  # noqa: E127
           (stm32.USB_HS,       'USB1',         0x40040000),
           (stm32.USB_HS,       'USB2',         0x40080000),
           (stm32h7.RCC,        'RCC_M7',       0x58024400),
           (stm32.ADC16,        'ADC3',         0x58026000, 3, 1),
           ]

# AP1 devices are ones accessible in the D3 domain; we can access these via AP1
# even if both CPU cores are down.
AP1DEVS = [(RAMDevice,          'SRAM4',        0x38000000, 0x00010000),
           (RAMDevice,          'Backup SRAM',  0x38800000, 0x00001000),
           (stm32h7.SYSCFG,     'SYSCFG',       0x58000400),
           (stm32.VREF,         'VREF',         0x58003C00),
           (stm32.GPIO,         'GPIOA',        0x58020000),
           (stm32.GPIO,         'GPIOB',        0x58020400),
           (stm32.GPIO,         'GPIOC',        0x58020800),
           (stm32.GPIO,         'GPIOD',        0x58020C00),
           (stm32.GPIO,         'GPIOE',        0x58021000),
           (stm32.GPIO,         'GPIOF',        0x58021400),
           (stm32.GPIO,         'GPIOG',        0x58021800),
           (stm32.GPIO,         'GPIOH',        0x58021C00),
           (stm32.GPIO,         'GPIOI',        0x58022000),
           (stm32.GPIO,         'GPIOJ',        0x58022400),
           (stm32.GPIO,         'GPIOK',        0x58022800),
           (stm32h7.RCC,        'RCC_D3',       0x58024400),
           (stm32h7.PWR,        'PWR',          0x58024800),
           (stm32.DMAMUX,       'DMAMUX2',      0x58025800, 8, 8),
           ]

# AP2 devices are accessible over the System Debug Bus.  This is mainly for the
# DBGMCU and other debug devices such as the breakpoint and trace units.
AP2DEVS = []

# AP3 devices are ones that we access via the M4 core.
AP3DEVS = [(stm32h7.ART,        'ART',          0x40024400),
           (stm32h7.RCC,        'RCC_M4',       0x58024400),
           (RAMDevice,          'SRAM1 ID M4',  0x10000000, 0x00020000),
           (RAMDevice,          'SRAM2 ID M4',  0x10020000, 0x00020000),
           (RAMDevice,          'SRAM3 ID M4',  0x10040000, 0x00008000),
           (RAMDevice,          'AXI SRAM M4',  0x24000000, 0x00080000),
           (RAMDevice,          'SRAM1 M4',     0x30000000, 0x00020000),
           (RAMDevice,          'SRAM2 M4',     0x30020000, 0x00020000),
           (RAMDevice,          'SRAM3 M4',     0x30040000, 0x00008000),
           ]


class STM32H7_DP(Target):
    def __init__(self, db):
        # Max SWD speed is:
        #   71.0 MHz for 2.70V < VDD < 3.6V
        #   52.5 MHz for 1.62V < VDD < 3.6V
        super().__init__(db, 52500000)
        self.m7_ap        = self.db.aps[0]
        self.m4_ap        = self.db.aps[3]
        self.apbd_ap      = self.db.aps[2]
        self.ahb_ap       = self.m7_ap
        self.uuid         = self.ahb_ap.read_bulk(0x1FF1E800, 12)
        self.flash_size   = (self.ahb_ap.read_32(0x1FF1E880) & 0x0000FFFF)*1024
        self.flash_nbanks = 2
        self.mcu_idcode   = dbgmcu.read_idc(db)

        for i, dl in enumerate((AP0DEVS, AP1DEVS, AP2DEVS, AP3DEVS)):
            ap = self.db.aps[i]

            for d in dl:
                cls  = d[0]
                name = d[1]
                addr = d[2]
                args = d[3:]
                cls(self, ap, name, addr, *args)

        self.flash = self.devs['FLASH']
        MemDevice(self, self.ahb_ap, 'FBANKS', self.flash.mem_base,
                  self.flash.flash_size)

    def __repr__(self):
        return 'STM32H7xx DP MCU_IDCODE 0x%08X' % self.mcu_idcode

    def get_fault_addr(self):
        return 0xA0000000

    def enable_and_measure_hse(self, nsamples=10):
        '''
        Measures the HSE to within around 100 kHz accuracy using TIM17.

        The RCC has an output, HSE_1MHZ that can be used to drive the RTC.
        When driving the RTC, HSE_1MHZ must be below 1 MHz, hence the name.
        HSE_1MHZ is generated by dividing HSE using the RTCPRE prescaler.
        While it is typically used to drive the RTC from HSE, HSE_1MHZ also has
        an input to TIM17 which allows us to indirectly measure the HSE
        frequency against the TIM17 kernel clock.

        The catch is that TIM17 will do a counter capture on *every single
        pulse* of HSE_1MHZ.  Even after chaining the max timer input capture
        divider and the max RTCPRE prescaler divider, that still only yields a
        frequency of HSE / 504 (or, a period of 12.6 us with a 40 MHz HSE
        crystal).  That's much too fast for us to poll via SWD, so we configure
        the DMA engine to sample the counter every time it pulses for a total
        of nsamples samples.  This is written to the start of SRAM1 and then we
        post-process the samples to determine the actual number of timer kernel
        clock cycles that elapsed during the measurement.

        Since we are going to manipulate the HSE_1MHZ prescaler, this method
        cannot be called if the RTC is currently being driven by HSE_1MHZ.

        The main problem with the accuracy of this measurement is that the HSI
        oscillator is not very stable and can yield results that would round up
        to 100 kHz in the wrong direction.  Typically you'll want to use this
        along with extra knowledge such as "the HSE will be a multiple of 1
        MHz" in order to get an exact value.

        As a result of measuring the HSE, the HSE will be enabled and it will
        be left enabled after this returns.
        '''
        rcc     = self.devs['RCC_M7']
        dmamux1 = self.devs['DMAMUX1']
        dma1    = self.devs['DMA1']
        tim17   = self.devs['TIM17']
        sram1   = self.devs['SRAM1 M7']

        # We must not be using HSE_1MHZ to drive the RTC.
        assert rcc._BDCR.RTCSEL != 3

        # Enable the HSE, and then configure HSE_1MHZ to the maximum divider of
        # HSE/63.
        rcc.enable_hse()
        rcc._CFGR.RTCPRE = 63

        # Before configuring DMA, we need to configure but not arm TIM17 in
        # order to clear any pending DMA requests from previous runs.
        # Specifically, we need to ensure that DIER.CC1DE is cleared BEFORE we
        # enable the DMA engine.
        rcc.enable_device('TIM17')
        tim17._CR1     = 0x00000000
        tim17._CCER    = 0x00000000
        tim17._DIER    = 0
        tim17._CCMR1_I = 0
        tim17._TISEL   = 2
        tim17._CCMR1_I = 0x0000000D
        tim17._ARR     = 0xFFFF
        tim17._CNT     = 0
        tim17._PSC     = 0
        tim17._SR      = 0

        # DMAMUX1 is always enabled; set channel 0 to be TIM17_CH1.
        dmamux1._C0CR = 111

        # Configure DMA1 to transfer 16 bits nsamples times from TIM17_CH1,
        # incrementing after each transfer.
        rcc.enable_device('DMA1')
        dma1._S0CR = 0x00000000
        while dma1._S0CR.read() & 1:
            pass
        dma1._LIFCR  = 0x0000003D
        dma1._S0CR   = 0x00002C00
        dma1._S0NDTR = nsamples
        dma1._S0PAR  = tim17._CCR1.addr
        dma1._S0M0AR = sram1.dev_base
        dma1._S0M1AR = 0x00000000
        dma1._S0FCR  = 0x00000000
        dma1._S0CR   = 0x00002C01

        # Finally, arm TIM17 to start capturing HSE/63 pulses.
        tim17._DIER  = 0x00000200
        tim17._CR1   = 0x00000001
        tim17._CCER  = 0x00000001

        # Wait for the DMA transfer to complete.
        while (dma1._LISR.read() & (1 << 5)) == 0:
            time.sleep(0.01)

        # Load each of the counter captures and sum their deltas.
        caps  = [sram1.ap.read_16(sram1.dev_base + i*2)
                 for i in range(nsamples)]
        ticks = 0
        for i in range(1, nsamples):
            ticks += ((caps[i] - caps[i-1]) & 0xFFFF)

        # We have a TIM17 input prescaler of 8, an HSE prescaler of 63,
        # nsamples-1 time deltas.  Given the timer frequency and the tick count
        # we can then estimate the HSE frequency.
        return 8 * 63 * (nsamples - 1) *rcc.f_timy_ker_ck / ticks

    @staticmethod
    def is_mcu(db):
        # APSEL 0, 1, 2 and 3 should be populated.
        # Probing is complicated by the fact that we can disable the M4 or the
        # M7 using the options registers.  When you disable a core, the AP
        # exists but is unprobeable and doesn't even identify as an AHB-AP, so
        # we don't even detect the CPU there in that configuration!  The core
        # will remain disabled until RCC_GCR.BOOTx is set to 1, after which
        # point presumably we would be able to probe the AHB-AP properly.  The
        # RCC is in the D3 domain, so it would be accessible via AP1 even if
        # both CPUs were disabled for some reason.  Note, however, that the MCU
        # doesn't allow both CPUs to be disabled via the flash option registers
        # and if both bits are turned off the MCU will still boot from the M7
        # core.  Finally, note that enabling all of the clocks in debug mode
        # via DBGMCU_CR doesn't allow us to probe the disabled CPUs despite
        # behaving similarly to a CPU stuck in a WFI instruction.
        #
        # AP0 is the Cortex-M7 and corresponds with db.cpus[0].
        # AP1 is the D3 AHB interconnect.
        # AP2 is the System Debug Bus (APB-D)
        # AP3 is the Cortex-M4 and corresponds with db.cpus[1].
        #
        # Note that other than the existence of AP3, a single-core H7 looks
        # exactly the same as a dual-core H7.  This might imply that we
        # shouldn't be treating them separately...
        if set(db.aps) != set((0, 1, 2, 3)):
            return False

        # APSEL 1 should be an AHB3 AP.
        if not isinstance(db.aps[1], psdb.access_port.AHB3AP):
            return False

        # APSEL 2 should be an APB AP.
        if not isinstance(db.aps[2], psdb.access_port.APBAP):
            return False

        # Identify the STM32H7 through the base component's CIDR/PIDR
        # registers using the System Debug Bus.
        c = db.aps[2].base_component
        if not c:
            c = db.aps[2].probe_components(match=False, recurse=False)
        if not c:
            return False
        if (c.addr, c.cidr, c.pidr) != (0xE00E0000, 0xB105100D, 0xA0450):
            return False

        # Finally, we can match on the DBGMCU IDC value.
        if dbgmcu.read_idc_dev_id(db) != 0x450:
            return False

        return True

    @staticmethod
    def pre_probe(db, verbose):
        # Ensure this is an STM32H7 DP part.
        if not STM32H7_DP.is_mcu(db):
            return

        # Enable all the clocks that we want to use.
        cr = dbgmcu.read_cr(db)
        if (cr & 0x0070003F) != 0x0070003F:
            if verbose:
                print('Detected STM32H7 DP, enabling all DBGMCU debug clocks.')
            dbgmcu.write_cr(db, cr | 0x0070003F)

    @staticmethod
    def probe(db):
        # Ensure this is an STM32H7 DP part.
        if not STM32H7_DP.is_mcu(db):
            return None

        # There should be two or fewer CPUs.
        if len(db.cpus) > 2:
            return None

        return STM32H7_DP(db)
