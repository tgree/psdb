# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from elftools.elf.elffile import ELFFile


class ELFBinary(object):
    '''
    Class used for reading the contents of an existing ELF file; typically used
    by flashing code to analyze an ELF executable and figure out which blocks
    of memory to be written where.
    '''
    def __init__(self, file_object):
        file_object.seek(0)
        self.elf_file = ELFFile(file_object)
        self.symtab   = self.elf_file.get_section_by_name('.symtab')
        self.entry    = self.elf_file['e_entry']
        self.pv_dv    = [(s['p_paddr'], s['p_vaddr'],
                          s.data() + b'\x00'*(s['p_memsz'] - s['p_filesz']))
                         for s in self.iter_segments()
                         if s['p_type'] == 'PT_LOAD'
                         ]
        self.flash_dv = [(s[0], s[2]) for s in self.pv_dv]

    @staticmethod
    def from_path(path):
        return ELFBinary(open(path, 'rb'))

    def iter_segments(self):
        return self.elf_file.iter_segments()

    def get_symbols_by_substring(self, substr):
        return [s for s in self.symtab.iter_symbols() if substr in s.name]

    def get_symbols_by_name(self, name):
        return [s for s in self.symtab.iter_symbols() if s.name == name]

    def get_symbol_by_name(self, name):
        s = self.get_symbols_by_name(name)
        assert len(s) == 1
        return s[0]

    def get_symbol_addr(self, sym):
        return self.get_symbol_by_name(sym)['st_value']

    def _read(self, addr, size, addr_index):
        for v in self.pv_dv:
            base = v[addr_index]
            data = v[2]
            if base <= addr and addr + size <= base + len(data):
                offset = addr - base
                return data[offset:offset + size]
        return None

    def read_p_addr(self, p_addr, size):
        return self._read(p_addr, size, 0)

    def read_v_addr(self, v_addr, size):
        return self._read(v_addr, size, 1)

    def read_symbol(self, sym, size):
        return self.read_v_addr(sym.entry.st_value, size)
