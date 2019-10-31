# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb
from .flash import FLASH
from ..device import MemDevice
from psdb.targets import Target


class STM32G4(Target):
    def __init__(self, db):
        super(STM32G4, self).__init__(db)
        self.ahb_ap     = self.db.aps[0]
        self.uuid       = self.ahb_ap.read_bulk(0x1FFF7590, 12)
        self.flash_size = (self.ahb_ap.read_32(0x1FFF75E0) & 0x0000FFFF)*1024
        self.mcu_idcode = self.ahb_ap.read_32(0xE0042000)
        self.flash      = FLASH(self, 'FLASH', 0x40022000, 0x00000000)
        MemDevice(self, 'FBANKS', self.flash.mem_base, self.flash.flash_size)

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
