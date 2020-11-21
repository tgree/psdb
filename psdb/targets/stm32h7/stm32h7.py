# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb
from psdb.devices import MemDevice, stm32h7
from psdb.targets import Target
from . import dbgmcu


class STM32H7(Target):
    def __init__(self, db):
        super(STM32H7, self).__init__(db, 24000000)
        self.ahb_ap     = self.db.aps[0]
        self.apbd_ap    = self.db.aps[2]
        self.uuid       = self.ahb_ap.read_bulk(0x1FF1E800, 12)
        self.flash_size = (self.ahb_ap.read_32(0x1FF1E880) & 0x0000FFFF)*1024
        self.mcu_idcode = dbgmcu.read_idc(db)
        self.flash      = stm32h7.FLASH_UP(self, self.ahb_ap, 'FLASH',
                                           0x52002000, 0x08000000, 3300000)
        MemDevice(self, self.ahb_ap, 'FBANKS', self.flash.mem_base,
                  self.flash.flash_size)

    def __repr__(self):
        return 'STM32H7xx MCU_IDCODE 0x%08X' % self.mcu_idcode

    @staticmethod
    def is_mcu(db):
        # APSEL 0, 1 and 2 should be populated.
        # AP0 is the Cortex-M7 and corresponds with db.cpus[0].
        # AP1 is the D3 AHB interconnect.
        # AP2 is the System Debug Bus (APB-D)
        if set(db.aps) != set((0, 1, 2)):
            return False

        # APSEL 0 should be an AHB AP.
        ap = db.aps[0]
        if not isinstance(ap, psdb.access_port.AHBAP):
            return False

        # APSEL 1 should be an AHB AP.
        if not isinstance(db.aps[1], psdb.access_port.AHBAP):
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
        # Ensure this is an STM32H7 part.
        if not STM32H7.is_mcu(db):
            return

        # Enable all the clocks that we want to use.
        cr = dbgmcu.read_cr(db)
        if (cr & 0x00700187) != 0x00700187:
            if verbose:
                print('Detected STM32H7, enabling all DBGMCU debug clocks.')
            dbgmcu.write_cr(db, cr | 0x00700187)

    @staticmethod
    def probe(db):
        # Ensure this is an STM32H7 part.
        if not STM32H7.is_mcu(db):
            return None

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        return STM32H7(db)
