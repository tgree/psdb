# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import psdb
from psdb.devices import MemDevice, RAMDevice, stm32g0
from psdb.targets import Target
from . import dbgmcu


# Verified with Nucleo-G071RB and V2J39S27 that flash writes work at 4 MHz, the
# fastest speed available on the STLINK-V2E debugger.
DEVICES = [
           (stm32g0.FLASH,  'FLASH',    0x40022000, 0x08000000, 4000000,
                                        0x1FFF7000, 1024),  # noqa: E127
           ]


class STM32G0(Target):
    def __init__(self, db):
        # Max SWD speed is not specified in the data sheet.
        super().__init__(db, 24000000)
        self.ahb_ap     = self.db.aps[0]
        self.uuid       = self.ahb_ap.read_bulk(0x1FFF7590, 12)
        self.flash_size = (self.ahb_ap.read_32(0x1FFF75E0) & 0x0000FFFF)*1024
        self.package    = self.ahb_ap.read_32(0x1FFF7500) & 0x0000000F
        self.mcu_idcode = self.ahb_ap.read_32(0x40015800)

        for d in DEVICES:
            cls  = d[0]
            name = d[1]
            addr = d[2]
            args = d[3:]
            cls(self, self.ahb_ap, name, addr, *args)

        self.flash = self.devs['FLASH']

        dev_id = (self.mcu_idcode & 0x0FFF)
        if dev_id == 0x460:
            # STM32G071xx and STM32G081xx
            if self.flash._OPTR.RAM_PARITY_CHECK:
                # Parity check disabled if RAM_PARITY_CHECK=1
                sram_len = 36 * 1024
            else:
                # Parity check enabled if RAM_PARITY_CHECK=0
                sram_len = 32 * 1024
        elif dev_id == 0x466:
            # STM32G031xx and STM32G041xx
            sram_len = 8 * 1024

        RAMDevice(self, self.ahb_ap, 'SRAM', 0x20000000, sram_len)
        MemDevice(self, self.ahb_ap, 'FBANKS', self.flash.mem_base,
                  self.flash.flash_size)
        MemDevice(self, self.ahb_ap, 'OTP', self.flash.otp_base,
                  self.flash.otp_len)

    def __repr__(self):
        return 'STM32G0 MCU_IDCODE 0x%08X' % self.mcu_idcode

    @staticmethod
    def is_mcu(db):
        # APSEL 0 should be populated.
        if set(db.aps) != set((0,)):
            return False

        # APSEL 0 should be an AHB3 AP.
        ap = db.aps[0]
        if not isinstance(ap, psdb.access_port.AHB3AP):
            return False

        # Identify the STM32G0 through the base component's CIDR/PIDR
        # registers.
        c = db.aps[0].base_component
        if not c:
            c = db.aps[0].probe_components(match=False, recurse=False)
        if not c:
            return False
        if c.cidr != 0xB105100D:
            return False
        if c.pidr != 0xA0460:
            return False

        # Unlike other ST MCUs, the IDCODE register returns 0 if we read it
        # while NRST is asserted, so we skip the DBGMCU check here.
        return True

    @staticmethod
    def probe(db):
        # Ensure this is an STM32G0 part.
        if not STM32G0.is_mcu(db):
            return

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        # We should be able to see the IDCODE now.
        if dbgmcu.read_idc_dev_id(db) not in (0x460, 0x466):
            return None

        # Enable all the clocks we want to use.
        cr = dbgmcu.read_cr(db)
        if (cr & 0x00000006) != 0x00000006:
            print('Detected STM32G0, enabling all DBGMCU debug clocks.')
            dbgmcu.write_cr(db, cr | 0x00000006)

        return STM32G0(db)
