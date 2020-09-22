# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb
from .rom_table_1 import STM32H7ROMTable1
from psdb.devices import MemDevice, stm32, stm32h7
from psdb.targets import Target


# AP0 devices are ones that we access via the M7 core.
AP0DEVS = [(MemDevice,          'M7 ITCM',      0x00000000, 0x00010000),
           (MemDevice,          'SRAM1 ID',     0x10000000, 0x00020000),
           (MemDevice,          'SRAM2 ID',     0x10020000, 0x00020000),
           (MemDevice,          'SRAM3 ID',     0x10040000, 0x00008000),
           (MemDevice,          'M7 DTCM',      0x20000000, 0x00020000),
           (MemDevice,          'AXI SRAM',     0x24000000, 0x00080000),
           (MemDevice,          'SRAM1',        0x30000000, 0x00020000),
           (MemDevice,          'SRAM2',        0x30020000, 0x00020000),
           (MemDevice,          'SRAM3',        0x30040000, 0x00008000),
           (MemDevice,          'Backup SRAM',  0x38800000, 0x00001000),
           (stm32.DAC,          'DAC1',         0x40007400),
           (stm32h7.TIM15,      'TIM15',        0x40014000),
           (stm32.DMA_DBM,      'DMA1',         0x40020000),
           (stm32.DMA_DBM,      'DMA2',         0x40020400),
           (stm32.DMAMUX,       'DMAMUX1',      0x40020800, 16, 8),
           (stm32h7.FLASH_DP,   'FLASH',        0x52002000, 0x08000000,
                                                3300000),  # noqa: E127
           (stm32h7.RCC,        'RCC_M7',       0x58024400),
           ]

# AP1 devices are ones accessible in the D3 domain; we can access these via AP1
# even if both CPU cores are down.
AP1DEVS = [(stm32.VREF,         'VREF',         0x58003C00),
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
AP3DEVS = [(stm32h7.RCC,        'RCC_M4',       0x58024400),
           ]


class STM32H7_DP(Target):
    def __init__(self, db):
        super(STM32H7_DP, self).__init__(db, 24000000)
        self.m7_ap      = self.db.aps[0]
        self.m4_ap      = self.db.aps[3]
        self.apbd_ap    = self.db.aps[2]
        self.ahb_ap     = self.m7_ap
        self.uuid       = self.ahb_ap.read_bulk(0x1FF1E800, 12)
        self.flash_size = (self.ahb_ap.read_32(0x1FF1E880) & 0x0000FFFF)*1024
        self.mcu_idcode = self.apbd_ap.read_32(0xE00E1000)

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

    @staticmethod
    def probe(db):
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
        # core.
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
            return None

        # APSEL 1 should be an AHB AP.
        if not isinstance(db.aps[1], psdb.access_port.AHBAP):
            return None

        # APSEL 2 should be an APB AP.
        if not isinstance(db.aps[2], psdb.access_port.APBAP):
            return None

        # Identify the STM32H7 through the base component's CIDR/PIDR
        # registers using the System Debug Bus.
        c = db.aps[2].base_component
        if not c or c.cidr != 0xB105100D or c.pidr != 0x00000000000A0450:
            return None

        # There should be two or fewer CPUs.
        if len(db.cpus) > 2:
            return None

        # Finally, we can match on the DBGMCU IDC value.
        rt1 = db.aps[2].base_component.find_components_by_type(STM32H7ROMTable1)
        assert len(rt1) == 1
        if (rt1[0].read_dbgmcu_idc() & 0x00000FFF) != 0x450:
            return None

        return STM32H7_DP(db)
