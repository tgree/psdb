# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
from ..device import Reg32
from ..stm32 import flash_type1

import time


class FLASH(flash_type1.FLASH):
    '''
    Driver for the FLASH device on the STM32WB55 series of MCUs.
    '''
    REGS = [Reg32('ACR',        0x00,   [('LATENCY',        3),
                                         ('',               5),
                                         ('PRFTEN',         1),
                                         ('ICEN',           1),
                                         ('DCEN',           1),
                                         ('ICRST',          1),
                                         ('DCRST',          1),
                                         ('',               2),
                                         ('PES',            1),
                                         ('EMPTY',          1),
                                         ]),
            Reg32('KEYR',       0x08,   [('KEY',            32)]),
            Reg32('OPTKEYR',    0x0C,   [('OPTKEY',         32)]),
            Reg32('SR',         0x10,   [('EOP',            1),
                                         ('OPERR',          1),
                                         ('',               1),
                                         ('PROGERR',        1),
                                         ('WRPERR',         1),
                                         ('PGAERR',         1),
                                         ('SIZERR',         1),
                                         ('PGSERR',         1),
                                         ('MISSERR',        1),
                                         ('FASTERR',        1),
                                         ('',               3),
                                         ('OPTNV',          1),
                                         ('RDERR',          1),
                                         ('OPTVERR',        1),
                                         ('BSY',            1),
                                         ('',               1),
                                         ('CFGBSY',         1),
                                         ('PESD',           1),
                                         ]),
            Reg32('CR',         0x14,   [('PG',             1),
                                         ('PER',            1),
                                         ('MER',            1),
                                         ('PNB',            8),
                                         ('',               5),
                                         ('STRT',           1),
                                         ('OPTSTRT',        1),
                                         ('FSTPG',          1),
                                         ('',               5),
                                         ('EOPIE',          1),
                                         ('ERRIE',          1),
                                         ('RDERRIE',        1),
                                         ('OBL_LAUNCH',     1),
                                         ('',               2),
                                         ('OPTLOCK',        1),
                                         ('LOCK',           1),
                                         ]),
            Reg32('ECCR',       0x18,   [('ADDR_ECC',       17),
                                         ('',               3),
                                         ('SYSF_ECC',       1),
                                         ('',               3),
                                         ('ECCCIE',         1),
                                         ('',               1),
                                         ('CPUID',          3),
                                         ('',               1),
                                         ('ECCC',           1),
                                         ('ECCD',           1),
                                         ]),
            Reg32('OPTR',       0x20,   [('RDP',            8),
                                         ('ESE',            1),
                                         ('BOR_LEV',        3),
                                         ('nRST_STOP',      1),
                                         ('nRST_STDBY',     1),
                                         ('nRST_SHDW',      1),
                                         ('',               1),
                                         ('IWDG_SW',        1),
                                         ('IWDG_STOP',      1),
                                         ('IWGD_STDBY',     1),
                                         ('WWDG_SW',        1),
                                         ('',               3),
                                         ('nBOOT1',         1),
                                         ('SRAM2_PE',       1),
                                         ('SRAM2_RST',      1),
                                         ('nSWBOOT0',       1),
                                         ('nBOOT0',         1),
                                         ('',               1),
                                         ('AGC_TRIM',       3),
                                         ]),
            Reg32('PCROP1ASR',  0x24,   [('PCROP1A_STRT',   9)]),
            Reg32('PCROP1AER',  0x28,   [('PCROP1A_END',    9),
                                         ('',               22),
                                         ('PCROP_RDP',      1),
                                         ]),
            Reg32('WRP1AR',     0x2C,   [('WRP1A_STRT',     8),
                                         ('',               8),
                                         ('WRP1A_END',      8),
                                         ]),
            Reg32('WRP1BR',     0x30,   [('WRP1B_STRT',     8),
                                         ('',               8),
                                         ('WRP1B_END',      8),
                                         ]),
            Reg32('PCROP1BSR',  0x34,   [('PCROP1B_STRT',   9)]),
            Reg32('PCROP1BER',  0x38,   [('PCROP1B_END',    9)]),
            Reg32('IPCCBR',     0x3C,   [('IPCCDBA',        14)]),
            Reg32('C2ACR',      0x5C,   [('',               8),
                                         ('PRFTEN',         1),
                                         ('ICEN',           1),
                                         ('',               1),
                                         ('ICRST',          1),
                                         ('',               3),
                                         ('PES',            1),
                                         ]),
            Reg32('C2SR',       0x60,   [('EOP',            1),
                                         ('OPERR',          1),
                                         ('',               1),
                                         ('PROGERR',        1),
                                         ('WRPERR',         1),
                                         ('PGAERR',         1),
                                         ('SIZERR',         1),
                                         ('PGSERR',         1),
                                         ('MISSERR',        1),
                                         ('FASTERR',        1),
                                         ('',               4),
                                         ('RDERR',          1),
                                         ('',               1),
                                         ('BSY',            1),
                                         ('',               1),
                                         ('CFGBSY',         1),
                                         ('PESD',           1),
                                         ]),
            Reg32('C2CR',       0x64,   [('PG',             1),
                                         ('PER',            1),
                                         ('MER',            1),
                                         ('PNB',            8),
                                         ('',               5),
                                         ('STRT',           1),
                                         ('',               1),
                                         ('FSTPG',          1),
                                         ('',               5),
                                         ('EOPIE',          1),
                                         ('ERRIE',          1),
                                         ('RDERRIE',        1),
                                         ]),
            Reg32('SFR',        0x80,   [('SFSA',           8),
                                         ('FSD',            1),
                                         ('',               3),
                                         ('DDS',            1),
                                         ]),
            Reg32('SRRVR',      0x84,   [('SBRV',           18),
                                         ('SBRSA',          5),
                                         ('BRSD',           1),
                                         ('',               1),
                                         ('SNBRSA',         5),
                                         ('NBRSD',          1),
                                         ('C2OPT',          1),
                                         ]),
            ]

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq,
                 otp_base, otp_len, **kwargs):
        super(FLASH, self).__init__(target, FLASH.REGS, 4096, ap, name,
                                    dev_base, mem_base, max_write_freq,
                                    otp_base, otp_len, **kwargs)

        optr = self._OPTR.read()
        if optr == 0:
            raise Exception('Unexpected OPTR=0, debug clocks may be disabled; '
                            'try using --srst')
        sfr = self._SFR.read()

        if (optr & (1 << 8)) and not (sfr & (1 << 8)):
            self.secure_flash_base = mem_base + ((sfr & 0x000000FF) * 4096)
        else:
            self.secure_flash_base = mem_base + self.target.flash_size
        self.user_flash_size = self.secure_flash_base - mem_base

        srrvr = self._SRRVR.read()
        if not (srrvr & (1 << 23)):
            self.user_sram2a_size = ((srrvr >> 18) & 0x1F)*1024
        else:
            self.user_sram2a_size = self.target.devs['SRAM2a'].size
        if not (srrvr & (1 << 30)):
            self.user_sram2b_size = ((srrvr >> 25) & 0x1F)*1024
        else:
            self.user_sram2b_size = self.target.devs['SRAM2b'].size

        # Clear OPTVERR if set; the MCU startup is buggy and some revisions
        # always set this bit even though there are no options problems.
        if self._SR.OPTVERR:
            self._SR.OPTVERR = 1

    def erase_all(self, verbose=True):
        '''
        Erases the entire user area of flash.
        '''
        return self.erase(self.mem_base, self.user_flash_size, verbose=verbose)

    def read_all(self):
        '''
        Reads the entire user area of flash.
        '''
        return self.read(self.mem_base, self.user_flash_size)

    def get_ipccdba(self):
        '''
        Returns the address of the IPCC mailbox data buffer.  Note that in the
        flash this value is stored as a double-word offset in SRAM2; here, we
        convert it to a full 32-bit address.
        '''
        offset = self._IPCCBR.IPCCDBA * 8
        return self.target.devs['SRAM2a'].dev_base + offset

    def set_boot_sram1(self, **kwargs):
        '''
        Configures the MCU to boot CPU1 from SRAM1 by updating the options
        register and writing it to flash.  The original options register value
        is returned for saving.
        '''
        return self.set_options({'nboot0'   : 0,
                                 'nswboot0' : 0,
                                 'nboot1'   : 0,
                                 }, **kwargs)

    def set_boot_sysmem(self, **kwargs):
        '''
        Configures the MCU to boot from system memory.
        '''
        return self.set_options({'nboot0'   : 1,
                                 'nswboot0' : 0,
                                 'nboot1'   : 1,
                                 }, **kwargs)

    def set_boot_flash(self, **kwargs):
        '''
        Configures the MCU to boot from flash.
        '''
        return self.set_options({'nboot0'   : 1,
                                 'nswboot0' : 1,
                                 'nboot1'   : 1,
                                 }, **kwargs)

    def is_sram_boot_enabled(self):
        options = self.get_options()
        return (options['nboot0']   == 0 and
                options['nswboot0'] == 0 and
                options['nboot1']   == 0)

    def is_flash_boot_enabled(self):
        options = self.get_options()
        return (options['nboot0']   == 1 and
                options['nswboot0'] == 1 and
                options['nboot1']   == 1)

    def get_st_otp_data_from_key(self, key):
        '''
        Searches the OTP memory for the 8-byte data identified by the specific
        key value.  This is an ST convention and probably not compatible with
        anything we do, but it is useful in the Nucleo boards.
        '''
        assert self.otp_len % 8 == 0

        data = self.read_otp(0, self.otp_len)
        while data:
            if data[-1] == key:
                return data[-8:]
            data = data[:-8]

        return None

    def set_wait_states(self, ws):
        '''
        Sets the number of wait states for the flash.  Should be configured as
        follows:

                |             HCLK4 (MHz)               |
             WS |   Vcore Range 1   |   Vcore Range 2   |
            ----+-------------------+-------------------+
             0  |    <= 18 MHz      |    <= 6 MHz       |
             1  |    <= 36 MHz      |    <= 12 MHz      |
             2  |    <= 54 MHz      |    <= 16 MHz      |
             3  |    <= 64 MHz      |       N/A         |
            ----+-------------------+-------------------+
        '''
        self._ACR.LATENCY = ws
        while self._ACR.LATENCY != ws:
            time.sleep(0.01)
