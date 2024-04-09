# Copyright (c) 2024 Phase Advanced Sensor Systems, Inc.
from ..device import Reg32, Reg32W, AReg32
from ..stm32 import flash_type1


class FLASH(flash_type1.FLASH):
    '''
    Driver for the FLASH device on the STM32C0 series of MCUs.
    '''
    REGS = [AReg32('ACR',           0x000, [('LATENCY',             0,  2),
                                            ('PRFTEN',              8),
                                            ('ICEN',                9),
                                            ('ICRST',               11),
                                            ('EMPTY',               16),
                                            ('DBG_SWEN',            18),
                                            ]),
            Reg32W('KEYR',          0x008),
            Reg32W('OPTKEYR',       0x00C),
            AReg32('SR',            0x010, [('EOP',                 0),
                                            ('OPERR',               1),
                                            ('PROGERR',             3),
                                            ('WRPERR',              4),
                                            ('PGAERR',              5),
                                            ('SIZERR',              6),
                                            ('PGSERR',              7),
                                            ('MISSERR',             8),
                                            ('FASTERR',             9),
                                            ('RDERR',               14),
                                            ('OPTVERR',             15),
                                            ('BSY',                 16),
                                            ('CFGBSY',              18),
                                            ]),
            AReg32('CR',            0x014, [('PG',                  0),
                                            ('PER',                 1),
                                            ('MER1',                2),
                                            ('PNB',                 3,  6),
                                            ('STRT',                16),
                                            ('OPTSTR',              17),
                                            ('FSTPG',               18),
                                            ('EOPIE',               24),
                                            ('ERRIE',               25),
                                            ('RDERRIE',             26),
                                            ('OBL_LAUNCH',          27),
                                            ('SEC_PROT',            28),
                                            ('OPTLOCK',             30),
                                            ('LOCK',                31),
                                            ]),
            AReg32('OPTR',          0x020, [('RDP',                 0,  7),
                                            ('BOR_EN',              8,),
                                            ('BOR_LEV',             9,  10),
                                            ('BORF_LEV',            11, 12),
                                            ('nRST_STOP',           13),
                                            ('nRST_STDBY',          14),
                                            ('nRST_SHDW',           15),
                                            ('IWDG_SW',             16),
                                            ('IWDG_STOP',           17),
                                            ('IWDG_STDBY',          18),
                                            ('WWDG_SW',             19),
                                            ('HSE_NOT_REMAPPED',    21),
                                            ('RAM_PARITY_CHECK',    22),
                                            ('SECURE_MUXING_EN',    23),
                                            ('nBOOT_SEL',           24),
                                            ('nBOOT1',              25),
                                            ('nBOOT0',              26),
                                            ('NRST_MODE',           27, 28),
                                            ('IRHEN',               29),
                                            ]),
            Reg32 ('PCROP1ASR',     0x024),
            Reg32 ('PCROP1AER',     0x028),
            Reg32 ('WRP1AR',        0x02C),
            Reg32 ('WRP1BR',        0x030),
            Reg32 ('PCROP1BSR',     0x034),
            Reg32 ('PCROP1BER',     0x038),
            AReg32('SECR',          0x080, [('SEC_SIZE',            0,  4),
                                            ('BOOT_LOCK',           16),
                                            ]),
            ]

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq,
                 otp_base, otp_len, **kwargs):
        super().__init__(target, FLASH.REGS, 2048, ap, name, dev_base,
                         mem_base, max_write_freq, otp_base, otp_len, **kwargs)

    def get_options(self):
        opts = super().get_options()
        opts['boot_lock'] = self._SECR.BOOT_LOCK
        return opts

    def set_options_no_connect(self, options, **kwargs):
        if 'boot_lock' in options:
            assert self.target.is_halted()
            with self._flash_unlocked():
                with self._options_unlocked():
                    self._SECR.BOOT_LOCK = options['boot_lock']
            del options['boot_lock']
        return super().set_options_no_connect(options, **kwargs)
