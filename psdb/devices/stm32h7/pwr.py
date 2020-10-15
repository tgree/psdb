# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32


class PWR(Device):
    '''
    Driver for the STM Power Control (PWR) device.
    '''
    REGS = [Reg32('CR1',        0x000, [('LPDS',        1),
                                        ('',            3),
                                        ('PVDE',        1),
                                        ('PLS',         3),
                                        ('DBP',         1),
                                        ('FLPS',        1),
                                        ('',            4),
                                        ('SVOS',        2),
                                        ('AVDEN',       1),
                                        ('ALS',         2),
                                        ]),
            Reg32('CSR1',       0x004, [('',            4),
                                        ('PVDO',        1),
                                        ('',            8),
                                        ('ACTVOSRDY',   1),
                                        ('ACTVOS',      2),
                                        ('AVDO',        1),
                                        ]),
            Reg32('CR2',        0x008, [('BREN',        1),
                                        ('',            3),
                                        ('MONEN',       1),
                                        ('',            11),
                                        ('BRRDY',       1),
                                        ('',            3),
                                        ('VBATL',       1),
                                        ('VBATH',       1),
                                        ('TEMPL',       1),
                                        ('TEMPH',       1),
                                        ]),
            Reg32('CR3',        0x00C, [('BYPASS',      1),
                                        ('LDOEN',       1),
                                        ('SDEN',        1),
                                        ('SDEXTHP',     1),
                                        ('SDLEVEL',     2),
                                        ('',            2),
                                        ('VBE',         1),
                                        ('VBRS',        1),
                                        ('',            6),
                                        ('SDEXTRDY',    1),
                                        ('',            7),
                                        ('USB33DEN',    1),
                                        ('USBREGEN',    1),
                                        ('USB33RDY',    1),
                                        ]),
            Reg32('CPU1CR',     0x010, [('PDDS_D1',     1),
                                        ('PDDS_D2',     1),
                                        ('PDDS_D3',     1),
                                        ('',            1),
                                        ('HOLD2F',      1),
                                        ('STOPF',       1),
                                        ('SBF',         1),
                                        ('SBF_D1',      1),
                                        ('SBF_D2',      1),
                                        ('CSSF',        1),
                                        ('HOLD2',       1),
                                        ('RUN_D3',      1),
                                        ]),
            Reg32('CPU2CR',     0x014, [('PDDS_D1',     1),
                                        ('PDDS_D2',     1),
                                        ('PDDS_D3',     1),
                                        ('',            1),
                                        ('HOLD1F',      1),
                                        ('STOPF',       1),
                                        ('SBF',         1),
                                        ('SBF_D1',      1),
                                        ('SBF_D2',      1),
                                        ('CSSF',        1),
                                        ('HOLD1',       1),
                                        ('RUN_D3',      1),
                                        ]),
            Reg32('D3CR',       0x018, [('',            13),
                                        ('VOSRDY',      1),
                                        ('VOS',         2),
                                        ]),
            Reg32('WKUPCR',     0x020, [('WKUPC1',      1),
                                        ('WKUPC2',      1),
                                        ('WKUPC3',      1),
                                        ('WKUPC4',      1),
                                        ('WKUPC5',      1),
                                        ('WKUPC6',      1),
                                        ]),
            Reg32('WKUPFR',     0x024, [('WKUPF1',      1),
                                        ('WKUPF2',      1),
                                        ('WKUPF3',      1),
                                        ('WKUPF4',      1),
                                        ('WKUPF5',      1),
                                        ('WKUPF6',      1),
                                        ]),
            Reg32('WKUPEPR',    0x028, [('WKUPEN1',     1),
                                        ('WKUPEN2',     1),
                                        ('WKUPEN3',     1),
                                        ('WKUPEN4',     1),
                                        ('WKUPEN5',     1),
                                        ('WKUPEN6',     1),
                                        ('',            2),
                                        ('WKUPP1',      1),
                                        ('WKUPP2',      1),
                                        ('WKUPP3',      1),
                                        ('WKUPP4',      1),
                                        ('WKUPP5',      1),
                                        ('WKUPP6',      1),
                                        ('',            2),
                                        ('WKUPPUPD1',   2),
                                        ('WKUPPUPD2',   2),
                                        ('WKUPPUPD3',   2),
                                        ('WKUPPUPD4',   2),
                                        ('WKUPPUPD5',   2),
                                        ('WKUPPUPD6',   2),
                                        ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(PWR, self).__init__(target, ap, addr, name, PWR.REGS, **kwargs)

    def _wait_vosrdy(self):
        while self._D3CR.VOSRDY == 0:
            time.sleep(0.01)

    def _set_vos(self, vos):
        # VOS numbers are in reverse... /facepalm
        self._D3CR.VOS = 4 - vos
        self._wait_vosrdy()

    def _get_vos(self):
        self._wait_vosrdy()
        return 4 - self._D3CR.VOS

    def set_vos(self, vos):
        rcc    = self.owner.devs['RCC_M7']
        syscfg = self.owner.devs['SYSCFG']
        rcc.enable_device('SYSCFG')

        curr_vos = self._get_vos()
        oden     = syscfg._PWRCR.ODEN
        if curr_vos == 1 and oden == 1:
            curr_vos = 0

        if curr_vos == vos:
            return

        if vos == 0:
            if curr_vos != 1:
                self._set_vos(1)
            syscfg._PWRCR.ODEN = 1
            self._wait_vosrdy()
        elif curr_vos == 0:
            syscfg._PWRCR.ODEN = 0
            self._wait_vosrdy()
            self._set_vos(vos)
        else:
            self._set_vos(vos)

    def set_mode_ldo(self):
        self._CR3 = 0x00000002
