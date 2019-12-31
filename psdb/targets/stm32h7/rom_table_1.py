# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb


DBGMCU_BASE = 0xE00E1000


class STM32H7ROMTable1(psdb.component.Component):
    '''
    Matcher for the STM32H7 System ROM Table 1.  This ROM table is found on
    AP2 at address 0xE00E0000.  In order to probe child components on AP2, we
    need to enable the D1/D3/Trace clocks via DBGMCU_CR.
    '''
    def __init__(self, component, subtype):
        super(STM32H7ROMTable1, self).__init__(component.parent, component.ap,
                                               component.addr, subtype)
        self.write_dbgmcu_cr(0x00700000)

    def read_dbgmcu_idc(self):
        return self.ap.read_32(DBGMCU_BASE + 0)

    def write_dbgmcu_cr(self, v):
        self.ap.write_32(v, DBGMCU_BASE + 4)


psdb.component.StaticMatcher(STM32H7ROMTable1, 2, 0xE00E0000,
                             0xB105100D, 0x00000000000A0450,
                             subtype='STM32H7 ROM Table 1')
