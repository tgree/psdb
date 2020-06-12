# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb
from .rom_table_1 import STM32H7ROMTable1
from psdb.devices import MemDevice, stm32h7
from psdb.targets import Target


class STM32H7(Target):
    def __init__(self, db):
        super(STM32H7, self).__init__(db, 24000000)
        self.ahb_ap     = self.db.aps[0]
        self.apbd_ap    = self.db.aps[2]
        self.uuid       = self.ahb_ap.read_bulk(0x1FF1E800, 12)
        self.flash_size = (self.ahb_ap.read_32(0x1FF1E880) & 0x0000FFFF)*1024
        self.mcu_idcode = self.apbd_ap.read_32(0xE00E1000)
        self.flash      = stm32h7.FLASH_UP(self, self.ahb_ap, 'FLASH',
                                           0x52002000, 0x08000000, 3300000)
        MemDevice(self, self.ahb_ap, 'FBANKS', self.flash.mem_base,
                  self.flash.flash_size)

    def __repr__(self):
        return 'STM32H7xx MCU_IDCODE 0x%08X' % self.mcu_idcode

    @staticmethod
    def probe(db):
        # APSEL 0 and 2 should be populated.
        if 0 not in db.aps:
            return None
        if 2 not in db.aps:
            return None

        # APSEL 0 should be an AHB AP.
        ap = db.aps[0]
        if not isinstance(ap, psdb.access_port.AHBAP):
            return None

        # APSEL 2 should be an APB AP.
        if not isinstance(db.aps[2], psdb.access_port.APBAP):
            return None

        # Identify the STM32H7 through the base component's CIDR/PIDR
        # registers.
        for ap in (db.aps[0], db.aps[2]):
            c = ap.base_component
            if not c or c.cidr != 0xB105100D or c.pidr != 0x00000000000A0450:
                return None

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        # Finally, we can match on the DBGMCU IDC value.
        rt1 = db.aps[2].base_component.find_components_by_type(STM32H7ROMTable1)
        assert len(rt1) == 1
        if (rt1[0].read_dbgmcu_idc() & 0x00000FFF) != 0x450:
            return None

        return STM32H7(db)
