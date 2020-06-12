# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import time

from ..device import Device, Reg32


class PWR(Device):
    '''
    Driver for the STM Power Control (PWR) device.
    '''
    REGS = [Reg32('CR1',        0x000,  [('LPMS',           3),
                                         ('',               1),
                                         ('FPDR',           1),
                                         ('FPDS',           1),
                                         ('',               2),
                                         ('DBP',            1),
                                         ('VOS',            2),
                                         ('',               3),
                                         ('LPR',            1),
                                         ]),
            Reg32('CR2',        0x004,  [('PVDE',           1),
                                         ('PLS',            3),
                                         ('PVME1',          1),
                                         ('',               1),
                                         ('PVME3',          1),
                                         ('',               3),
                                         ('USV',            1),
                                         ]),
            Reg32('CR3',        0x008,  [('EWUP1',          1),
                                         ('EWUP2',          1),
                                         ('EWUP3',          1),
                                         ('EWUP4',          1),
                                         ('EWUP5',          1),
                                         ('',               3),
                                         ('EBORHSMPSFB',    1),
                                         ('RRS',            1),
                                         ('APC',            1),
                                         ('ECRPE',          1),
                                         ('EBLEA',          1),
                                         ('E802A',          1),
                                         ('EC2H',           1),
                                         ('EIWUL',          1),
                                         ]),
            Reg32('CR4',        0x00C,  [('WP1',            1),
                                         ('WP2',            1),
                                         ('WP3',            1),
                                         ('WP4',            1),
                                         ('WP5',            1),
                                         ('',               3),
                                         ('VBE',            1),
                                         ('VBRS',           1),
                                         ('',               5),
                                         ('C2BOOT',         1),
                                         ]),
            Reg32('SR1',        0x010,  [('WUF1',           1),
                                         ('WUF2',           1),
                                         ('WUF3',           1),
                                         ('WUF4',           1),
                                         ('WUF5',           1),
                                         ('',               2),
                                         ('SMPSFBF',        1),
                                         ('BORHF',          1),
                                         ('BLEWUF',         1),
                                         ('802WUF',         1),
                                         ('CRPEF',          1),
                                         ('BLEAF',          1),
                                         ('802AF',          1),
                                         ('C2HF',           1),
                                         ('WUFI',           1),
                                         ]),
            Reg32('SR2',        0x014,  [('SMPSBF',         1),
                                         ('SMPSF',          1),
                                         ('',               6),
                                         ('REGLPS',         1),
                                         ('REGLPF',         1),
                                         ('VOSF',           1),
                                         ('PVDO',           1),
                                         ('PVMO1',          1),
                                         ('',               1),
                                         ('PVMO3',          1),
                                         ]),
            Reg32('SCR',        0x018),
            Reg32('CR5',        0x01C,  [('SMPSVOS',        4),
                                         ('SMPSSC',         3),
                                         ('',               1),
                                         ('BORHC',          1),
                                         ('',               6),
                                         ('SMPSEN',         1),
                                         ]),
            Reg32('PUCRA',      0x020),
            Reg32('PDCRA',      0x024),
            Reg32('PUCRB',      0x028),
            Reg32('PDCRB',      0x02C),
            Reg32('PUCRC',      0x030),
            Reg32('PDCRC',      0x034),
            Reg32('PUCRD',      0x038),
            Reg32('PDCRD',      0x03C),
            Reg32('PUCRE',      0x040),
            Reg32('PDCRE',      0x044),
            Reg32('PUCRH',      0x058),
            Reg32('PDCRH',      0x05C),
            Reg32('C2CR1',      0x080,  [('LPMS',           3),
                                         ('',               1),
                                         ('FPDR',           1),
                                         ('FPDS',           1),
                                         ('',               8),
                                         ('BLEEWKUP',       1),
                                         ('802EWKUP',       1),
                                         ]),
            Reg32('C2CR3',      0x084,  [('EWUP1',          1),
                                         ('EWUP2',          1),
                                         ('EWUP3',          1),
                                         ('EWUP4',          1),
                                         ('EWUP5',          1),
                                         ('',               4),
                                         ('EBLEWUP',        1),
                                         ('E802WUP',        1),
                                         ('',               1),
                                         ('APC',            1),
                                         ('',               2),
                                         ('EIWUL',          1),
                                         ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(PWR, self).__init__(target, ap, addr, name, PWR.REGS, **kwargs)

    def enable_cpu2_boot(self):
        self._CR4.C2BOOT = 1

    def is_cpu2_boot_enabled(self):
        return self._CR4.C2BOOT != 0

    def enable_backup_domain(self):
        self._CR1.DBP = 1
        while self._CR1.DBP == 0:
            time.sleep(0.01)

    def set_voltage_scaling(self, vos):
        '''
        Set the voltage range, which is 1-based:

            Range 1: 1.2 V, up to 64 MHz
            Range 2: 1.0 V, up to 16 MHz
        '''
        assert vos in (1, 2)
        self._CR1.VOS = vos
        while self._SR2.VOSF:
            time.sleep(0.01)
