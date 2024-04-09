# Copyright (c) 2019-2024 Phase Advanced Sensor Systems, Inc.
import psdb
from psdb.devices import MemDevice, RAMDevice, stm32l4
from psdb.targets import Target
from . import dbgmcu


DEVICES = [(RAMDevice,      'SRAM2 S', 0x10000000, 0x00002000),
           (RAMDevice,      'SRAM1',   0x20000000, 0x00008000),
           (RAMDevice,      'SRAM2',   0x20008000, 0x00002000),
           (stm32l4.FLASH,  'FLASH',   0x40022000, 0x08000000, 4000000,
                                       0x1FFF7000, 1024),  # noqa: E127
           ]


class STM32L4(Target):
    def __init__(self, db):
        # Max SWD speed is not specified in the data sheet.
        super().__init__(db, 24000000)
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
                  self.flash.flash_size)
        MemDevice(self, self.ahb_ap, 'OTP', self.flash.otp_base,
                  self.flash.otp_len)

    def __repr__(self):
        return 'STM32L4 MCU_IDCODE 0x%08X' % self.mcu_idcode

    @staticmethod
    def is_mcu(db):
        # Only APSEL 0 should be populated.
        if set(db.aps) != set((0,)):
            return False

        # APSEL 0 should be an AHB3 AP.
        ap = db.aps[0]
        if not isinstance(ap, psdb.access_port.AHB3AP):
            return False

        # Identify the STM32L4 through the base component's CIDR/PIDR
        # registers.
        c = db.aps[0].base_component
        if not c:
            c = db.aps[0].probe_components(match=False, recurse=False)
        if not c:
            return False
        if c.cidr != 0xB105100D:
            return False
        if c.pidr != 0xA0464:
            return False

        # Finally, we can match on the DBGMCU IDC value.
        if dbgmcu.read_idc_dev_id(db) != 0x464:
            return False

        return True

    @staticmethod
    def pre_probe(db, verbose):
        # Ensure this is an STM32L4 part.
        if not STM32L4.is_mcu(db):
            return

        # Enable all the clocks we want to use.
        cr = dbgmcu.read_cr(db)
        if (cr & 0x00000007) != 0x00000007:
            if verbose:
                print('Detected STM32L4, enabling all DBGMCU debug clocks.')
            dbgmcu.write_cr(db, cr | 0x00000007)

    @staticmethod
    def probe(db):
        # Ensure this is an STM32L4 part.
        if not STM32L4.is_mcu(db):
            return None

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        return STM32L4(db)
