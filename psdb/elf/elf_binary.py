# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from elftools.elf.elffile import ELFFile


class ELFBinary(object):
    '''
    Class used for reading the contents of an existing ELF file; typically used
    by flashing code to analyze an ELF executable and figure out which blocks
    of memory to be written where.
    '''
    def __init__(self, path):
        self.path     = path
        self.bin_file = open(self.path, 'rb')
        self.elf_file = ELFFile(self.bin_file)
        self.symtab   = self.elf_file.get_section_by_name('.symtab')
        self.entry    = self.elf_file['e_entry']
        self.flash_dv = [(s['p_paddr'], s.data() +
                          b'\x00'*(s['p_memsz'] - s['p_filesz']))
                         for s in self.iter_segments()
                         if s['p_type'] == 'PT_LOAD'
                         ]

    def iter_segments(self):
        return self.elf_file.iter_segments()

    def get_symbol_by_name(self, sym):
        s = [s for s in self.symtab.iter_symbols() if s.name == sym]
        assert len(s) == 1
        return s[0]

    def get_symbol_addr(self, sym):
        return self.get_symbol_by_name(sym)['st_value']
