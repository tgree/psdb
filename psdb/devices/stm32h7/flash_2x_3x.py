# Copyright (c) 2018-2025 Phase Advanced Sensor Systems, Inc.
from .flash import FLASH
from ..device import RegDiv, Reg32, Reg32R


class FLASH_2x_3x(FLASH):
    '''
    Driver for the FLASH device on the STM32H72x/3x series of single-core MCUs.
    '''
    OPT_REGS = [RegDiv('---Options'),
                Reg32 ('OPTSR_CUR',     0x01C, [('OPT_BUSY',        1),
                                                ('',                1),
                                                ('BOR_LEV',         2),
                                                ('IWDG1_SW',        1),
                                                ('',                1),
                                                ('NRST_STOP_D1',    1),
                                                ('NRST_STDY_D1',    1),
                                                ('RDP',             8),
                                                ('',                1),
                                                ('IWDG_FZ_STOP',    1),
                                                ('IWDG_FZ_SDBY',    1),
                                                ('ST_RAM_SIZE',     2),
                                                ('SECURITY',        1),
                                                ('',                7),
                                                ('IO_HSLV',         1),
                                                ('OPTCHANGEERR',    1),
                                                ('',                1),
                                                ]),
                Reg32 ('OPTSR_PRG',     0x020, [('',                2),
                                                ('BOR_LEV',         2),
                                                ('IWDG1_SW',        1),
                                                ('',                1),
                                                ('NRST_STOP_D1',    1),
                                                ('NRST_STDY_D1',    1),
                                                ('RDP',             8),
                                                ('',                1),
                                                ('IWDG_FZ_STOP',    1),
                                                ('IWDG_FZ_SDBY',    1),
                                                ('ST_RAM_SIZE',     2),
                                                ('SECURITY',        1),
                                                ('',                7),
                                                ('IO_HSLV',         1),
                                                ('',                2),
                                                ]),
                Reg32R('PRAR_CUR',      0x028),
                Reg32 ('PRAR_PRG',      0x02C),
                Reg32R('SCAR_CUR',      0x030),
                Reg32 ('SCAR_PRG',      0x034),
                Reg32R('WPSN_CUR',      0x038),
                Reg32 ('WPSN_PRG',      0x03C),
                Reg32R('BOOT_CURR',     0x040),
                Reg32 ('BOOT_PRG',      0x044),
                Reg32 ('OPTSR2_CUR',    0x070, [('TCM_AXI_SHARED',  2),
                                                ('CPUFREQ_BOOST',   1),
                                                ]),
                Reg32 ('OPTSR2_PRG',    0x074, [('TCM_AXI_SHARED',  2),
                                                ('CPUFREQ_BOOST',   1),
                                                ]),
                ]

    def __init__(self, target, ap, name, dev_base, mem_base,
                 max_nowait_write_freq, **kwargs):
        super().__init__(target, ap, name, dev_base, mem_base,
                         max_nowait_write_freq, FLASH_2x_3x.OPT_REGS, **kwargs)

    def get_options_reg(self):
        '''Returns the contents of the options registers.'''
        return ((self._OPTSR_CUR.read() << 32) | self._OPTSR2_CUR.read())

    def get_options(self):
        '''
        Returns the set of currently-active options from the OPTSR_CUR register.
        '''
        optsr_cur = self._OPTSR_CUR.read()
        options1 = {
            name.lower() : ((optsr_cur >> shift) & ((1 << width) - 1))
            for name, (width, shift) in self._OPTSR_PRG.reg.fields_map.items()
        }
        optsr2_cur = self._OPTSR2_CUR.read()
        options2 = {
            name.lower() : ((optsr2_cur >> shift) & ((1 << width) - 1))
            for name, (width, shift) in self._OPTSR2_PRG.reg.fields_map.items()
        }
        options = {**options1, **options2}
        options['boot'] = self._BOOT_CURR.read()
        return options

    def _flash_options(self, new_optsr_prg, new_optsr2_prg, new_boot,
                       verbose=True):
        '''Records the new options values in flash.'''
        assert self.target.is_halted()
        old_optsr_cur  = self._OPTSR_CUR.read()
        old_optsr2_cur = self._OPTSR2_CUR.read()
        if verbose:
            print('Flashing options (Old OPTSR_CUR=0x%08X, Target '
                  'OPTSR_PRG=0x%08X)' % (old_optsr_cur, new_optsr_prg))
            print('                 (Old OPTSR2_CUR=0x%08X, Target '
                  'OPTSR2_PRG=0x%08X)' % (old_optsr2_cur, new_optsr2_prg))
        with self._options_unlocked():
            self._OPTSR_PRG  = new_optsr_prg
            self._OPTSR2_PRG = new_optsr2_prg
            if new_boot is not None:
                self._BOOT_PRG = new_boot
            self._OPTCR.OPTSTART = 1
            while self._OPTSR_CUR.OPT_BUSY:
                pass
        if verbose:
            print('Flash completed (OPTSR_CUR=0x%08X, OPTSR_PRG=0x%08X)' %
                  (self._OPTSR_CUR.read(), self._OPTSR_PRG.read()))
            print('                (OPTSR2_CUR=0x%08X, OPTSR2_PRG=0x%08X)' %
                  (self._OPTSR2_CUR.read(), self._OPTSR2_PRG.read()))

    def set_options(self, options,
                    verbose=True,                # pylint: disable=W0613
                    connect_under_reset=False):  # pylint: disable=W0613
        '''
        This sets the specified option bits in the OPTSR_PRG register and then
        triggers an option-byte load.  No reset takes place, but for
        compatibility with other STM devices, the idiom for invoking
        set_options is:

            target = target.flash.set_options({...})
        '''
        boot_prg = options.get('boot', None)
        if boot_prg is not None:
            del options['boot']

        optsr_prg = self._OPTSR_PRG.read()
        for name, (width, shift) in self._OPTSR_PRG.reg.fields_map.items():
            value = options.get(name.lower(), None)
            if value is None:
                continue

            assert value <= ((1 << width) - 1)
            optsr_prg &= ~(((1 << width) - 1) << shift)
            optsr_prg |= (value << shift)
            del options[name.lower()]

        optsr2_prg = self._OPTSR2_PRG.read()
        for name, (width, shift) in self._OPTSR2_PRG.reg.fields_map.items():
            value = options.get(name.lower(), None)
            if value is None:
                continue

            assert value <= ((1 << width) - 1)
            optsr2_prg &= ~(((1 << width) - 1) << shift)
            optsr2_prg |= (value << shift)
            del options[name.lower()]

        if options:
            raise Exception('Invalid options: %s' % options)

        self._flash_options(optsr_prg, optsr2_prg, boot_prg)
        return self.target
