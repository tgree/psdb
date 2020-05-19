# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import types


class Reg(object):
    READABLE  = (1 << 0)
    WRITEABLE = (1 << 1)

    def __init__(self, name, offset, size, flags, fields):
        self.name   = name
        self.offset = offset
        self.size   = size
        self.flags  = flags
        self.fields = fields
        if size is not None:
            nbits       = sum(f[1] for f in fields)
            assert(nbits <= size*8)
            if nbits < size*8:
                self.fields = self.fields + [('', size*8 - nbits)]

        self.fields_map = {}
        shift           = 0
        for f in fields:
            if f[0]:
                assert f[0] not in self.fields_map
                self.fields_map[f[0]] = (f[1], shift)
            shift += f[1]


class RegDiv(Reg):
    def __init__(self, name):
        super(RegDiv, self).__init__(name, None, None, 0, [])


class Reg32(Reg):
    def __init__(self, name, offset, fields=[]):
        super(Reg32, self).__init__(name, offset, 4,
                                    Reg.READABLE | Reg.WRITEABLE, fields)

    def read(self, dev):
        return dev._read_32(self.offset)

    def write(self, dev, v):
        dev._write_32(v, self.offset)


class Reg32R(Reg):
    def __init__(self, name, offset, fields=[]):
        super(Reg32R, self).__init__(name, offset, 4, Reg.READABLE, fields)

    def read(self, dev):
        return dev._read_32(self.offset)


class Reg32W(Reg):
    def __init__(self, name, offset, fields=[]):
        super(Reg32W, self).__init__(name, offset, 4, Reg.WRITEABLE, fields)

    def write(self, dev, v):
        dev._write_32(v, self.offset)

class RDCapture(object):
    def __init__(self, reg, dev):
        assert 'val' not in reg.fields_map
        object.__setattr__(self, 'reg', reg)
        object.__setattr__(self, 'dev', dev)

    def __getattr__(self, name):
        if name == 'val':
            return self.read()

        width, shift = self.reg.fields_map[name]
        return self.dev._get_field(width, shift, self.reg.offset)

    def __setattr__(self, name, v):
        if name == 'val':
            self.write(v)
            return

        width, shift = self.reg.fields_map[name]
        self.dev._set_field(v, width, shift, self.reg.offset)

    def read(self):
        return self.reg.read(self.dev)

    def write(self, v):
        self.reg.write(self.dev, v)


class Device(object):
    def __init__(self, target, ap, dev_base, name, regs):
        self.target   = target
        self.ap       = ap
        self.dev_base = dev_base
        self.name     = name
        self.regs     = regs
        for r in regs:
            n = r.name.lower()
            if r.flags & Reg.READABLE:
                m = types.MethodType(lambda s, o=r.offset: s._read_32(o), self)
                self.__dict__['_read_' + n] = m
            if r.flags & Reg.WRITEABLE:
                m = types.MethodType(lambda s, v, o=r.offset: s._write_32(v, o),
                                     self)
                self.__dict__['_write_' + n] = m
            self.__dict__['_' + n.upper()] = RDCapture(r, self)

        assert self.name not in self.target.devs
        self.target.devs[self.name] = self

    def _read_32(self, offset):
        return self.ap.read_32(self.dev_base + offset)

    def _write_32(self, v, offset):
        self.ap.write_32(v, self.dev_base + offset)

    def _set_field(self, v, width, shift, offset):
        assert width + shift <= 32
        mask = (1 << width) - 1
        assert ((v & ~mask) == 0)
        curr = self._read_32(offset)
        curr &= ~(mask << shift)
        curr |= (v << shift)
        self._write_32(curr, offset)

    def _get_field(self, width, shift, offset):
        assert width + shift <= 32
        mask = (1 << width) - 1
        curr = self._read_32(offset) >> shift
        return curr & mask

    def dump_registers(self):
        width = max(len(r.name) for r in self.regs if r.flags & Reg.READABLE)

        for r in self.regs:
            if r.flags & Reg.READABLE:
                print('%*s = 0x%0*X' % (width, r.name, 2*r.size, r.read(self)))

    def enable_device(self):
        self.target._enable_device(self)


class MemDevice(Device):
    '''
    Base class for memory-type devices (SRAM, Flash, etc.).
    '''
    def __init__(self, target, ap, name, addr, size):
        super(MemDevice, self).__init__(target, ap, addr, name, [])
        self.size = size

    def read_mem_block(self, addr, size):
        return self.ap.read_bulk(addr, size)
