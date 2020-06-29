# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import struct

from .mmap import MemMap
from .note import NoteSection
from ..util import round_up_pow_2


class Core:
    EHDR_FORMAT = '<8B8xHHLLLLLHHHHHH'
    EHDR_SIZE   = struct.calcsize(EHDR_FORMAT)

    PHDR_FORMAT = '<LLLLLLLL'
    PHDR_SIZE   = struct.calcsize(PHDR_FORMAT)

    SHDR_FORMAT = '<LLLLLLLLLL'
    SHDR_SIZE   = struct.calcsize(SHDR_FORMAT)

    def __init__(self):
        self.mmaps = []
        self.notes = []

    @property
    def phoff(self):
        return Core.EHDR_SIZE if self.mmaps else 0

    @property
    def shoff(self):
        return self.phoff + (1 + len(self.mmaps))*Core.PHDR_SIZE

    def _write_elf_header(self, f):
        data = struct.pack(Core.EHDR_FORMAT,
                           0x7F, ord('E'), ord('L'), ord('F'),
                           1,                # e_ident[4] = ELFCLASS32
                           1,                # e_ident[5] = ELFDATA2LSB
                           1,                # e_ident[6] = EV_CURRENT
                           0x40,             # e_ident[7] = ELFOSABI_ARM_AEABI
                           4,                # e_type     = ET_CORE
                           40,               # e_machine  = EM_ARM
                           1,                # e_version  = EV_CURRENT
                           0,                # e_entry
                           self.phoff,       # e_phoff
                           0,                # e_shoff
                           0,                # e_flags
                           Core.EHDR_SIZE,   # e_ehsize
                           Core.PHDR_SIZE,   # e_phentsize
                           len(self.notes) +
                           len(self.mmaps),  # e_phnum
                           Core.SHDR_SIZE,   # e_shentsize
                           0,                # e_shnum
                           0                 # e_shstrndx
                           )
        f.write(data)

    def _write_pt_note_phdr(self, f, p_offset, note_data):
        data = struct.pack(Core.PHDR_FORMAT,
                           4,               # ptype = PT_NOTE
                           p_offset,
                           0x00000000,      # p_vaddr
                           0x00000000,      # p_paddr
                           len(note_data),  # p_filesz
                           0,               # p_memsz
                           0x4,             # p_flags = r
                           1,               # p_align
                           )
        f.write(data)

    def _write_pt_load_phdr(self, f, mmap, p_offset):
        data = struct.pack(Core.PHDR_FORMAT,
                           1,               # p_type = PT_LOAD
                           p_offset,        # p_offset
                           mmap.addr,       # p_vaddr
                           0,               # p_paddr
                           len(mmap.data),  # p_filesz
                           len(mmap.data),  # p_memsz
                           0x7,             # p_flags = rwx
                           1,               # p_align
                           )
        f.write(data)

    def add_mem_map(self, addr, data):
        '''
        Adds the specified chunk of data to the core at the specified virtual
        address.
        '''
        self.mmaps.append(MemMap(addr, data))

    def add_thread(self, regs, pid=1, sig=6):
        '''
        Adds a thread.  The registers are either a 17- or 18-entry array with
        the following contents, depending on if FPSCR is included or not:

            [r0, ..., r15, xpsr, <fpscr>]
        '''
        ns = NoteSection()
        ns.add_prpsinfo('xtalx', 'xtalx')
        ns.add_prstatus(pid, sig, regs)
        self.notes.append(ns)

    def write(self, path):
        '''
        Writes the core file to the specified path.
        '''
        with open(path, 'wb') as f:
            self.write_to_file_object(f)

    def write_to_file_object(self, f):
        '''
        Writes the core file to the specified file-like object.  It should be
        opened in binary format.
        '''
        # Compute the length of all combined headers and then find where the
        # data offset would be from there based on the data alignment.
        hdr_size    = (Core.EHDR_SIZE +
                       len(self.notes)*Core.PHDR_SIZE +
                       len(self.mmaps)*Core.PHDR_SIZE)
        note_offset = hdr_size
        note_size   = sum([len(n.data) for n in self.notes])
        data_align  = 1
        data_offset = round_up_pow_2(hdr_size + note_size, data_align)

        # Start with the ELF header.
        self._write_elf_header(f)

        # Now, write each PT_NOTE header.
        pos = note_offset
        for n in self.notes:
            self._write_pt_note_phdr(f, pos, n.data)
            pos += len(n.data)

        # Now, write a PT_LOAD header for each memory mapping.
        pos = data_offset
        for m in self.mmaps:
            self._write_pt_load_phdr(f, m, pos)
            pos += round_up_pow_2(len(m.data), data_align)

        # Now, write the PT_NOTE sections.
        for n in self.notes:
            f.write(n.data)

        # Now, write the memory mappings themselves.
        pos = hdr_size + note_size
        assert pos == f.tell()
        for m in self.mmaps:
            pos = f.tell()
            pad = round_up_pow_2(pos, data_align) - pos
            f.write(b'\x00'*pad)
            f.write(m.data)
