# Copyright (c) 2021 by Phase Advanced Sensor Systems, Inc.
import psdb
from psdb.devices import MemDevice, RAMDevice, stm32, stm32u5
from psdb.targets import Target
from . import dbgmcu


# Verified with Nucleo-U575ZIQ and V3J7M3B0S0 that flash writes faster than 3.3
# MHz error out.  After upgrading to V3J10M3B0S0, unfortunately it still errors
# out when writing faster than 8 MHz, so we leave the max write speed at 3.3
# MHz for now and have a hack in the stlink_v3.py file to enable 8 MHz if it
# sees a U5.  In that configuration the V3E can flash at around 90 K/s; the
# WB55 XTSWD achieves around 94 K/s at 16 MHz.
DEVICES = [
           (MemDevice,       'System ROM',  0x0BF90000, 0x00008000),
           (RAMDevice,       'SRAM1',       0x20000000, 0x00030000),
           (RAMDevice,       'SRAM2',       0x20030000, 0x00010000),
           (RAMDevice,       'SRAM3',       0x20040000, 0x00080000),
           (RAMDevice,       'SRAM4',       0x28000000, 0x00004000),
           (stm32.GPT32,     'TIM2',        0x40000000),
           (stm32.GPT32,     'TIM3',        0x40000400),
           (stm32.GPT32,     'TIM4',        0x40000800),
           (stm32.GPT32,     'TIM5',        0x40000C00),
           (stm32.BT,        'TIM6',        0x40001000),
           (stm32u5.I2C,     'I2C1',        0x40005400),
           (stm32u5.I2C,     'I2C2',        0x40005800),
           (stm32u5.I2C,     'I2C4',        0x40008400),
           (stm32.ACT,       'TIM1',        0x40012C00),
           (stm32.CORDIC,    'CORDIC',      0x40021000),
           (stm32u5.FLASH,   'FLASH',       0x40022000, 0x08000000, 3300000,
                                            0x0BFA0000, 512),  # noqa: E127
           (RAMDevice,       'Backup SRAM', 0x40036400, 0x00000800),
           (stm32.GPIO,      'GPIOA',       0x42020000),
           (stm32.GPIO,      'GPIOB',       0x42020400),
           (stm32.GPIO,      'GPIOC',       0x42020800),
           (stm32.GPIO,      'GPIOD',       0x42020C00),
           (stm32.GPIO,      'GPIOE',       0x42021000),
           (stm32.GPIO,      'GPIOF',       0x42021400),
           (stm32.GPIO,      'GPIOG',       0x42021800),
           (stm32.GPIO,      'GPIOH',       0x42021C00),
           (stm32.GPIO,      'GPIOI',       0x42022000),
           (stm32.ADC14,     'ADC1',        0x42028000, 1, 1),
           (stm32.USB_HS,    'USB1',        0x42040000),
           (stm32u5.I2C,     'I2C3',        0x46002800),
           (stm32u5.RTC,     'RTC',         0x46007800),
           (stm32u5.PWR,     'PWR',         0x46020800),
           (stm32u5.RCC,     'RCC',         0x46020C00),
           (stm32.DAC,       'DAC',         0x46021800),
           (stm32.GPDMA,     'GPDMA',       0x50020000),
           (stm32u5.DBGMCU,  'DBGMCU',      0xE0044000),
           ]


class STM32U5MCU(psdb.component.Component):
    def __init__(self, component, subtype):
        super().__init__(component.parent, component.ap, component.addr,
                         'STM32U5 MCU')


class STM32U5(Target):
    def __init__(self, db):
        # Max SWD speed is:
        #   66.5 MHz for 2.70V < VDD < 3.6V
        #   43.0 MHz for 1.71V < VDD < 3.6V
        super().__init__(db, 43000000)
        self.ahb_ap     = self.db.aps[0]
        self.uuid       = self.ahb_ap.read_bulk(0x0BFA0700, 12)
        self.flash_size = (self.ahb_ap.read_32(0x0BFA07A0) & 0x0000FFFF)*1024
        self.package    = self.ahb_ap.read_32(0x0BFA0500) & 0x0000001F
        self.mcu_idcode = self.ahb_ap.read_32(0xE0044000)

        dev_id = (self.mcu_idcode & 0x0FFF)
        if dev_id != 0x482:
            raise Exception('Unrecognized MCU_IDCODE 0x%08X' % self.mcu_idcode)

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
        return 'STM32U5 MCU_IDCODE 0x%08X' % self.mcu_idcode

    @staticmethod
    def is_mcu(db):
        # Only APSEL 0 should be populated.
        if set(db.aps) != set((0,)):
            return False

        # APSEL 0 should be an AHB5 AP
        ap = db.aps[0]
        if not isinstance(ap, psdb.access_port.AHB5AP):
            return False

        # Identify the STM32U5 through the base component's CIDR/PIDR.
        c = db.aps[0].base_component
        if not c:
            c = db.aps[0].probe_components(match=False, recurse=False)
        if not c:
            return False
        if (c.addr, c.cidr, c.pidr) != (0xE00FE000, 0xB105100D, 0xA0482):
            return False

        # Finally, we can match on the DBGMCU IDC value.
        if dbgmcu.read_idc_dev_id(db) != 0x482:
            return False

        return True

    @staticmethod
    def pre_probe(db, verbose):
        # Ensure this is an STM32U5 part.
        if not STM32U5.is_mcu(db):
            return

        # Enable all the clocks we want to use.
        cr = dbgmcu.read_cr(db)
        if (cr & 0x00000026) != 0x00000026:
            if verbose:
                print('Detected STM32U5, enabling all DBGMCU debug clocks.')
            dbgmcu.write_cr(db, cr | 0x00000026)

    @staticmethod
    def probe(db):
        # Ensure this is an STM32U5 part.
        if not STM32U5.is_mcu(db):
            return None

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        return STM32U5(db)


psdb.component.StaticMatcher(STM32U5MCU, 0, 0xE00FE000, 0xB105100D,
                             0x00000000000A0482, subtype='STM32U5 MCU')
