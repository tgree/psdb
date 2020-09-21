# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .flash import FLASH
from ..device import Reg32, Reg32R


class FLASH_DP(FLASH):
    '''
    Driver for the FLASH device on the STM32H7xx series of dual-core MCUs.
    '''
    OPT_REGS = [Reg32 ('OPTSR_CUR',     0x01C, [('OPT_BUSY',        1),
                                                ('',                1),
                                                ('BOR_LEV',         2),
                                                ('IWDG1_SW',        1),
                                                ('IWDG2_SW',        1),
                                                ('NRST_STOP_D1',    1),
                                                ('NRST_STDY_D1',    1),
                                                ('RDP',             8),
                                                ('',                1),
                                                ('IWDG_FZ_STOP',    1),
                                                ('IWDG_FZ_SDBY',    1),
                                                ('ST_RAM_SIZE',     2),
                                                ('SECURITY',        1),
                                                ('BOOT_CM4',        1),
                                                ('BOOT_CM7',        1),
                                                ('NRST_STOP_D2',    1),
                                                ('NRST_STBY_D2',    1),
                                                ('',                3),
                                                ('IO_HSLV',         1),
                                                ('OPTCHANGEERR',    1),
                                                ('SWAP_BANK_OPT',   1),
                                                ]),
                Reg32 ('OPTSR_PRG',     0x020, [('',                2),
                                                ('BOR_LEV',         2),
                                                ('IWDG1_SW',        1),
                                                ('IWDG2_SW',        1),
                                                ('NRST_STOP_D1',    1),
                                                ('NRST_STDY_D1',    1),
                                                ('RDP',             8),
                                                ('',                1),
                                                ('IWDG_FZ_STOP',    1),
                                                ('IWDG_FZ_SDBY',    1),
                                                ('ST_RAM_SIZE',     2),
                                                ('SECURITY',        1),
                                                ('BOOT_CM4',        1),
                                                ('BOOT_CM7',        1),
                                                ('NRST_STOP_D2',    1),
                                                ('NRST_STBY_D2',    1),
                                                ('',                3),
                                                ('IO_HSLV',         1),
                                                ('',                1),
                                                ('SWAP_BANK_OPT',   1),
                                                ]),
                Reg32R('PRAR_CUR1',     0x028),
                Reg32 ('PRAR_PRG1',     0x02C),
                Reg32R('SCAR_CUR1',     0x030),
                Reg32 ('SCAR_PRG1',     0x034),
                Reg32R('WPSN_CUR1R',    0x038),
                Reg32 ('WPSN_PRG1R',    0x03C),
                Reg32R('BOOT7_CURR',    0x040),
                Reg32 ('BOOT7_PRGR',    0x044),
                Reg32R('BOOT4_CURR',    0x048),
                Reg32 ('BOOT4_PRGR',    0x04C),
                Reg32R('PRAR_CUR2',     0x128),
                Reg32 ('PRAR_PRG2',     0x12C),
                Reg32R('SCAR_CUR2',     0x130),
                Reg32 ('SCAR_PRG2',     0x134),
                Reg32R('WPSN_CUR2R',    0x138),
                Reg32 ('WPSN_PRG2R',    0x13C),
                ]

    def __init__(self, target, ap, name, dev_base, mem_base, max_write_freq,
                 **kwargs):
        super(FLASH_DP, self).__init__(target, ap, name, dev_base, mem_base,
                                       max_write_freq, FLASH_DP.OPT_REGS,
                                       **kwargs)

    def get_options_reg(self):
        '''Returns the contents of the options register.'''
        return self._OPTSR_CUR.read()

    def get_options(self):
        '''
        Returns the set of currently-active options from the OPTSR_CUR register.
        '''
        optsr_cur = self._OPTSR_CUR.read()
        return {name.lower() : ((optsr_cur >> shift) & ((1 << width) - 1))
                for name, (width, shift) in
                self._OPTSR_PRG.reg.fields_map.items()}

    def _flash_options(self, new_optsr_prg, verbose=True):
        '''Records the new options values in flash.'''
        assert self.target.is_halted()
        old_optsr_cur = self._OPTSR_CUR.read()
        if verbose:
            print('Flashing options (Old OPTSR_CUR=0x%08X, Target '
                  'OPTSR_PRG=0x%08X)' % (old_optsr_cur, new_optsr_prg))
        with self._options_unlocked():
            self._OPTSR_PRG      = new_optsr_prg
            self._OPTCR.OPTSTART = 1
            while self._OPTSR_CUR.OPT_BUSY:
                pass
        if verbose:
            print('Flash completed (OPTSR_CUR=0x%08X, OPTSR_PRG=0x%08X)' %
                  (self._OPTSR_CUR.read(), self._OPTSR_PRG.read()))

    def set_options(self, options, verbose=True, connect_under_reset=False):
        '''
        This sets the specified option bits in the OPTSR_PRG register and then
        triggers an option-byte load.  No reset takes place, but for
        compatibility with other STM devices, the idiom for invoking
        set_options is:

            target = target.flash.set_options({...})
        '''
        optsr_prg = self._OPTSR_PRG.read()
        for name, (width, shift) in self._OPTSR_PRG.reg.fields_map.items():
            value = options.get(name.lower(), None)
            if value is None:
                continue

            assert value <= ((1 << width) - 1)
            optsr_prg &= ~(((1 << width) - 1) << shift)
            optsr_prg |= (value << shift)
            del options[name.lower()]

        if options:
            raise Exception('Invalid options: %s' % options)

        self._flash_options(optsr_prg)
        return self.target
