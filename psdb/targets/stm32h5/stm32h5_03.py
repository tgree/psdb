# Copyright (c) 2026 Phase Advanced Sensor Systems, Inc.
import psdb
from psdb.devices import MemDevice, RAMDevice, stm32h5
from psdb.targets import Target
from . import dbgmcu


DEVICES = [
        (MemDevice,         'System ROM',   0x0BF80000, 0x00010000),
        (RAMDevice,         'SRAM1',        0x20000000, 0x00004000),
        (RAMDevice,         'SRAM2',        0x20004000, 0x00004000),
        (stm32h5.FLASH_03,  'FLASH',        0x40022000, 0x08000000, 3300000,
                                            0x08FFF000, 2048),  # noqa: E127
        (stm32h5.PWR_03,    'PWR',          0x44020800),
        (stm32h5.RCC_03,    'RCC',          0x44020C00),
        ]


class STM32H5_03_MCU(psdb.component.Component):
    def __init__(self, component, subtype):
        super().__init__(component.parent, component.ap, component.addr,
                         'STM32H503 MCU')


class STM32H5_03(Target):
    def __init__(self, db):
        # Max SWD speed is:
        #   80 MHz for 2.70V < VDD < 3.6V
        #   71 MHz for 1.71V < VDD < 3.6V
        super().__init__(db, 71000000)
        self.apb_ap     = self.db.aps[0]
        self.ahb_ap     = self.db.aps[1]
        self.uuid       = self.ahb_ap.read_bulk(0x08FFF800, 12)
        memsz_pkg       = self.ahb_ap.read_32(0x08FFF80C)
        self.flash_size = (memsz_pkg & 0x0000FFFF) * 1024
        self.package    = (memsz_pkg >> 16) & 0x0000001F
        self.mcu_idcode = dbgmcu.read_idc(db)

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
        return 'STM32H503'

    @staticmethod
    def is_mcu(db):
        # APSEL 0 and 1 should be populated.
        # AP0 is the System Debug access port.
        # AP1 is the Cortex-M33 debug access port.
        if set(db.aps) != set((0, 1)):
            return False

        # APSEL 0 should be an APB AP.
        if not isinstance(db.aps[0], psdb.access_port.APBAP):
            return False

        # APSEL 1 should be an AHB3 AP.
        if not isinstance(db.aps[1], psdb.access_port.AHB3AP):
            return False

        # Identify the STM32H503 through the base component's CIDR/PIDR
        # registers usinged the System Debug Bus.
        c = db.aps[0].base_component
        if not c:
            c = db.aps[0].probe_components(match=False, recurse=False)
        if not c:
            return False
        if (c.addr, c.cidr, c.pidr) != (0xE00E0000, 0xB105100D, 0x001A0474):
            return False

        # Finally, we can match on the DBGMCU IDC value.
        if dbgmcu.read_idc_dev_id(db) != 0x474:
            return False

        return True

    @staticmethod
    def pre_probe(db, verbose):
        # Ensure this is an STM32H503 part.
        if not STM32H5_03.is_mcu(db):
            return

        # Enable all the clocks that we want to use.
        cr = dbgmcu.read_cr(db)
        if (cr & 0x00000026) != 0x00000026:
            if verbose:
                print('Detected STM32H503, enabling all DBGMCU debug clocks.')
            dbgmcu.write_cr(db, cr | 0x00000026)

    @staticmethod
    def probe(db):
        # Ensure this is an STM32H503 part.
        if not STM32H5_03.is_mcu(db):
            return None

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        return STM32H5_03(db)


psdb.component.StaticMatcher(STM32H5_03_MCU, 1, 0xE00FE000, 0xB105100D,
                             0x00000000001A0474, subtype='STM32H503 MCU')
