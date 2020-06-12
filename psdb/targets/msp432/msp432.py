# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb
from psdb.devices import MemDevice, msp432
from psdb.targets import Target


DEVICES = [(msp432.FLCTL,  'FLCTL',    0x40011000, 0x00201108),
           ]


class MSP432P401(Target):
    def __init__(self, db):
        super(MSP432P401, self).__init__(db, 3300000)
        self.ahb_ap = self.db.aps[0]

        for d in DEVICES:
            cls  = d[0]
            name = d[1]
            addr = d[2]
            args = d[3:]
            cls(self, self.ahb_ap, name, addr, *args)

        self.flash = self.devs['FLCTL']
        MemDevice(self, self.ahb_ap, 'FBANK0', self.flash.mem_base,
                  self.flash.flash_size)

    def __repr__(self):
        return 'MSP432P401'

    @staticmethod
    def probe(db):
        '''
        Discover an MSP432 target.  This is what the component tree looks like
        for an MSP432P401R:

          Found AHB AP 0 [8b 16b 32b] with IDR 0x24770011 (BASE 0xE00FF003)
          Found MEM AP 4 [32b] with IDR 0x11770001 (BASE 0x00000000)
          Found Cortex-M4 CPU
          Component 'AHB AP 0 [8b 16b 32b]':0xE00FF000:0xB105100D:
                                            0x000000000B1979AF MT 0x00000001
            Component 'AHB AP 0 [8b 16b 32b]':0xE000E000:0xB105E00D:
                                              0x00000004000BB00C MT 0x00000000
            Component 'AHB AP 0 [8b 16b 32b]':0xE0001000:0xB105E00D:
                                              0x00000004003BB002 MT 0x00000000
            Component 'AHB AP 0 [8b 16b 32b]':0xE0002000:0xB105E00D:
                                              0x00000004002BB003 MT 0x00000000
            Component 'AHB AP 0 [8b 16b 32b]':0xE0000000:0xB105E00D:
                                              0x00000004003BB001 MT 0x00000000
            Component 'AHB AP 0 [8b 16b 32b]':0xE0040000:0xB105900D:
                                              0x00000004000BB9A1 MT 0x00000011
        '''
        # APSEL 0 should be populated.
        if 0 not in db.aps:
            return None

        # APSEL 0 should be an AHB AP.
        ap = db.aps[0]
        if not isinstance(ap, psdb.access_port.AHBAP):
            return None

        # Identify the MSP432P401 through the base component's CIDR/PIDR
        # registers.
        c = db.aps[0].base_component
        if not c or c.cidr != 0xB105100D or c.pidr != 0x000000000B1979AF:
            return None

        # There should be exactly one CPU.
        if len(db.cpus) != 1:
            return None

        return MSP432P401(db)
