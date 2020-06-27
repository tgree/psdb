# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import struct


class Note:
    '''
    A note starts with a note header, which is then followed by the note name
    as a string padded out to a multiple of 4 bytes and finally by the note
    contents which is also padded to a multiple of 4 bytes.  The format looks
    something like this:

        uint32_t    n_namesz; // Size of name including single NULL-terminator
        uint32_t    n_descsz; // Size of descriptor data following padded name
        uint32_t    n_type;   // Type, i.e. NT_PRSTATUS
        char        name[n_namesz];
        char        pad[n_namesz to multiple of 4];
        n_type      descriptor_data;
        char        pad[n_descsz to multiple of 4];
    '''
    def __init__(self, name, note_type, descriptor):
        self.name       = name
        self.note_type  = note_type
        self.descriptor = descriptor

    def serialize(self):
        data = struct.pack('<LLL', len(self.name) + 1, len(self.descriptor),
                           self.note_type)
        data += self.name.encode() + b'\x00'
        while len(data) % 4:
            data += b'\x00'
        data += self.descriptor
        while len(data) % 4:
            data += b'\x00'

        return data


class NoteSection:
    def __init__(self):
        self.notes = []
        self.data  = b''

    def add_note(self, name, note_type, descriptor):
        n = Note(name, note_type, descriptor)
        self.notes.append(n)
        self.data += n.serialize()

    def add_prstatus(self, pid, sig, regs):
        '''
        Adds an NT_PRSTATUS note to the section.  The regs should be an array
        of 17 values with the following contents:

            [r0, ..., r15, xpsr]

        It's really confusing about what all registers can actually go in here.
        Useful sources:

            1. Linux kernel: arch/arm/include/uapi/asm/ptrace.h
            2. Google coredumper: trunk/src/elfcore.h
            3. binutils-gdb: gdb/arch/arm.h
            4. /usr/include on arm: grep for the prstatus struct.

        It looks like there should actually be 18 values but it isn't clear
        what the 18th register would be.  'info regs' in gdb only displays
        17 registers.
        '''
        assert len(regs) == 17
        data = struct.pack('<12xH10xL44x17LLL', sig, pid, *regs, 0, 0)
        assert len(data) == 148
        self.add_note('CORE', 1, data)

    def add_prpsinfo(self, name, cmdline):
        '''
        Adds an NT_PRPSINFO note to the section.  We include only the process
        name and initial command line.
        '''
        data = struct.pack('<28x15sx79sx', name.encode(), cmdline.encode())
        assert len(data) == 124
        self.add_note('CORE', 3, data)
