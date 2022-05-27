# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.


def convert_positional_to_adjacency(fields):
    '''
    Converts a set of fields of the form:

        ('NAME', bit_pos_0, bit_pos_1)

    or:

        ('NAME', bit_pos)

    into the adjacency format expected by the Reg constructor, including
    inserting padding fields as necessary.  Note that bit_pos_0 <= bit_pos_1,
    i.e. the lower-numbered bit comes first.
    '''
    sorted_fields    = sorted(fields, key=lambda f: f[1])
    pos              = 0
    generated_fields = []
    for f in sorted_fields:
        # Sanity that the start is ordered properly.
        assert pos <= f[1]

        # Convert 1-bit fields to N-bit fields.
        if len(f) == 2:
            f = (f[0], f[1], f[1])

        # Sanity that the bounds are ordered properly.
        assert f[2] >= f[1]

        # Eat any unused bits.
        if pos < f[1]:
            generated_fields.append(('', f[1] - pos))
            pos = f[1]

        # Generate the field.
        generated_fields.append((f[0], f[2] - f[1] + 1))

        # Advance the position.
        pos = f[2] + 1

    return generated_fields


class ReadCommand:
    def __init__(self, ap, addr, size):
        self.ap   = ap
        self.addr = addr
        self.size = size


class Reg(object):
    READABLE     = (1 << 0)
    WRITEABLE    = (1 << 1)
    SIDE_EFFECTS = (1 << 2)

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
        super().__init__(name, None, None, 0, [])


class Reg32(Reg):
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, 4, Reg.READABLE | Reg.WRITEABLE, fields)

    def read(self, dev):
        return dev._read_32(self.offset)

    def read_cmd(self, dev):
        return dev._read_32_cmd(self.offset)

    def write(self, dev, v):
        dev._write_32(v, self.offset)


class Reg32R(Reg):
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, 4, Reg.READABLE, fields)

    def read(self, dev):
        return dev._read_32(self.offset)

    def read_cmd(self, dev):
        return dev._read_32_cmd(self.offset)


class Reg32W(Reg):
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, 4, Reg.WRITEABLE, fields)

    def write(self, dev, v):
        dev._write_32(v, self.offset)


class Reg32S(Reg):
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, 4,
                         Reg.WRITEABLE | Reg.READABLE | Reg.SIDE_EFFECTS,
                         fields)

    def read(self, dev):
        return dev._read_32(self.offset)

    def read_cmd(self, dev):
        return dev._read_32_cmd(self.offset)

    def write(self, dev, v):
        dev._write_32(v, self.offset)


class Reg32RS(Reg):
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, 4, Reg.READABLE | Reg.SIDE_EFFECTS,
                         fields)

    def read(self, dev):
        return dev._read_32(self.offset)

    def read_cmd(self, dev):
        return dev._read_32_cmd(self.offset)


class Reg8(Reg):
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, 1, Reg.READABLE | Reg.WRITEABLE, fields)

    def read(self, dev):
        return dev._read_8(self.offset)

    def read_cmd(self, dev):
        return dev._read_8_cmd(self.offset)

    def write(self, dev, v):
        dev._write_8(v, self.offset)


class Reg8S(Reg):
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, 1,
                         Reg.READABLE | Reg.WRITEABLE | Reg.SIDE_EFFECTS,
                         fields)

    def read(self, dev):
        return dev._read_8(self.offset)

    def read_cmd(self, dev):
        return dev._read_8_cmd(self.offset)

    def write(self, dev, v):
        dev._write_8(v, self.offset)


class AReg32(Reg32):
    '''
    Same as Reg32 but uses first and last bit positions rather than length.
    '''
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, convert_positional_to_adjacency(fields))


class AReg32R(Reg32R):
    '''
    Same as Reg32R but uses first and last bit positions rather than length.
    '''
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, convert_positional_to_adjacency(fields))


class AReg32W(Reg32W):
    '''
    Same as Reg32W but uses first and last bit positions rather than length.
    '''
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, convert_positional_to_adjacency(fields))


class AReg32S(Reg32S):
    '''
    Same as Reg32S but uses first and last bit positions rather than length.
    '''
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, convert_positional_to_adjacency(fields))


class AReg32RS(Reg32RS):
    '''
    Same as Reg32RS but uses first and last bit positions rather than length.
    '''
    def __init__(self, name, offset, fields=[]):
        super().__init__(name, offset, convert_positional_to_adjacency(fields))


class RDCapture(object):
    def __init__(self, reg, dev, dev_base):
        object.__setattr__(self, 'reg', reg)
        object.__setattr__(self, 'dev', dev)
        object.__setattr__(self, 'addr', dev_base + reg.offset)

    def __getattr__(self, name):
        try:
            width, shift = self.reg.fields_map[name]
            return self.dev._get_field(width, shift, self.reg.offset)
        except KeyError:
            pass

        raise AttributeError

    def __setattr__(self, name, v):
        try:
            width, shift = self.reg.fields_map[name]
            self.dev._set_field(v, width, shift, self.reg.offset)
            return
        except KeyError:
            pass

        raise AttributeError

    def __bool__(self):
        raise Exception("Don't test an RDCapture!")

    def __equals__(self, other):
        raise Exception("Don't compare an RDCapture!")

    def read(self):
        return self.reg.read(self.dev)

    def write(self, v):
        self.reg.write(self.dev, v)


class Device(object):
    def __init__(self, owner, ap, dev_base, name, regs, path=None):
        super(Device, self).__setattr__(
                'reg_map', {'_' + r.name.upper() : RDCapture(r, self, dev_base)
                            for r in regs if not isinstance(r, RegDiv)})

        self.ap       = ap
        self.dev_base = dev_base
        self.name     = name
        self.path     = path or name
        self.regs     = regs
        self.owner    = owner

        assert self.name not in self.owner.devs
        self.owner.devs[self.name] = self

    def __getattr__(self, name):
        try:
            return self.reg_map[name]
        except KeyError:
            pass

        raise AttributeError('No such attribute: "%s"' % name)

    def __setattr__(self, name, value):
        if name[0] == '_' and name.upper() == name:
            rd = self.reg_map[name]
            if isinstance(value, RDCapture):
                rd.write(value.read())
            else:
                rd.write(value)
        else:
            super(Device, self).__setattr__(name, value)

    def _read_8(self, offset):
        return self.ap.read_8(self.dev_base + offset)

    def _read_8_cmd(self, offset):
        return ReadCommand(self.ap, self.dev_base + offset, 1)

    def _read_32(self, offset):
        return self.ap.read_32(self.dev_base + offset)

    def _read_32_cmd(self, offset):
        return ReadCommand(self.ap, self.dev_base + offset, 4)

    def _write_8(self, v, offset):
        self.ap.write_8(v, self.dev_base + offset)

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


class MemDevice(Device):
    '''
    Base class for memory-type devices.
    '''
    def __init__(self, target, ap, name, addr, size, **kwargs):
        super(MemDevice, self).__init__(target, ap, addr, name, [], **kwargs)
        self.size = size

    def read_mem_block(self, addr, size):
        return self.ap.read_bulk(addr, size)


class RAMDevice(MemDevice):
    '''
    Base class for RAM-style devices.
    '''
    def __init__(self, target, ap, name, addr, size, **kwargs):
        super().__init__(target, ap, name, addr, size, **kwargs)
        self.owner.ram_devs[self.name] = self

    def write_mem_block(self, data, addr):
        self.ap.write_bulk(data, addr)
