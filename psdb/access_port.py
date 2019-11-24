# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from .component import Component

import struct


class AP(object):
    def __init__(self, db, ap_num, idr):
        super(AP, self).__init__()
        self.db      = db
        self.ap_num  = ap_num
        self.idr     = idr
        self.verbose = False

    def __repr__(self):
        return 'AP %u' % self.ap_num

    def read_idr(self):
        return self.db.read_ap_reg(self.ap_num, 0xFC)


class MemAP(AP):
    FLAG_SIZE_8  = (1<<0)
    FLAG_SIZE_16 = (1<<1)
    FLAG_SIZE_32 = (1<<2)
    SIZE_TABLE = {
            0 : FLAG_SIZE_8,
            1 : FLAG_SIZE_16,
            2 : FLAG_SIZE_32,
            }
    MASK_TABLE = {
            0 : 0x000000FF,
            1 : 0x0000FFFF,
            2 : 0xFFFFFFFF,
            }
    FLAGS_TABLE = {
            FLAG_SIZE_8  :  '8b',
            FLAG_SIZE_16 :  '16b',
            FLAG_SIZE_32 :  '32b',
            }

    def __init__(self, db, ap_num, idr, csw_base, typ='MEM'):
        super(MemAP, self).__init__(db, ap_num, idr)
        self.typ            = typ
        self.flags          = MemAP.FLAG_SIZE_32
        assert ((self.idr >> 13) & 0xF) == 0x8
        self.csw_reset      = self._read_csw()
        self.csw_base       = csw_base or (self.csw_reset & 0xFFFFF008)
        self.csw_size       = self.csw_reset & 0x00000007
        self.csw_ainc       = self.csw_reset & 0x00000030
        self.csw            = -1
        self.tar            = self._read_tar()

    def __repr__(self):
        features = [MemAP.FLAGS_TABLE[f]
                    for f in MemAP.FLAGS_TABLE if self.flags & f]
        return '%s AP %u [%s]' % (self.typ, self.ap_num, ' '.join(features))

    def read_32(self, addr):
        return self.db.read_32(addr, self.ap_num)

    def read_16(self, addr):
        return self.db.read_16(addr, self.ap_num)

    def read_8(self, addr):
        return self.db.read_8(addr, self.ap_num)

    def read_bulk(self, addr, size):
        return self.db.read_bulk(addr, size, self.ap_num)

    def write_32(self, v, addr):
        self.db.write_32(v, addr, self.ap_num)

    def write_16(self, v, addr):
        self.db.write_16(v, addr, self.ap_num)

    def write_8(self, v, addr):
        self.db.write_8(v, addr, self.ap_num)

    def write_bulk(self, data, addr):
        self.db.write_bulk(data, addr, self.ap_num)

    def probe_components(self, verbose=False):
        self.base_component = Component.probe(self, self._read_base())
        if self.base_component:
            if verbose:
                print('  %s' % self.base_component)
            self.base_component.probe_children(verbose=verbose)

    def _probe_sizes(self):
        '''
        Warning!  You can't just probe any old MemAP... on the MSP432 there is
        some weird second MemAP and when you probe it it seems to reset the
        target CPU and hold it in reset.  Only call this for target types where
        it is known to be safe.
        '''
        for v, f in MemAP.SIZE_TABLE.items():
            if self.flags & f:
                continue

            self._write_csw(self.csw_base | v)
            if (self._read_csw() & 0x7) == v:
                self.flags |= f

        assert self.flags & MemAP.FLAG_SIZE_32
        self._write_csw(self.csw_reset)

    def _read_csw(self):
        return self.db.read_ap_reg(self.ap_num, 0x00)

    def _read_tar(self):
        return self.db.read_ap_reg(self.ap_num, 0x04)

    def _read_drw(self):
        return self.db.read_ap_reg(self.ap_num, 0x0C)

    def _read_bd(self, index):
        return self.db.read_ap_reg(self.ap_num, 0x10 + 4*index)

    def _read_mbt(self):
        return self.db.read_ap_reg(self.ap_num, 0x20)

    def _read_cfg(self):
        return self.db.read_ap_reg(self.ap_num, 0xF4)

    def _read_base(self):
        return self.db.read_ap_reg(self.ap_num, 0xF8)

    def _write_csw(self, val):
        if self.csw == val:
            return
        if self.verbose:
            print('Changing csw to 0x%08X' % val)
        self.db.write_ap_reg(self.ap_num, 0x00, val)
        self.csw      = val
        self.csw_size = val & 0x7
        self.csw_ainc = (val >> 4) & 0x3

    def _write_tar(self, val):
        if self.verbose:
            print('Changing tar from 0x%08X to 0x%08X' % (self.tar, val))
        self.db.write_ap_reg(self.ap_num, 0x04, val)
        self.tar = val

    def _write_drw(self, val):
        self.db.write_ap_reg(self.ap_num, 0x0C, val)

    def _write_bd(self, val, index):
        self.db.write_ap_reg(self.ap_num, 0x10 + 4*index, val)

    def _read_generic(self, addr, size):
        flag = MemAP.SIZE_TABLE[size]
        assert self.flags & flag
        if self.csw_size != size:
            self._write_csw(self.csw_base | size)
        if self.tar != addr:
            self._write_tar(addr)
        v = self._read_drw()
        if self.csw_ainc == 1:
            self.tar += (1 << size)
        return ((v >> 8*(addr % 4)) & MemAP.MASK_TABLE[size])

    def _read_8(self, addr):
        return self._read_generic(addr, 0)

    def _read_16(self, addr):
        return self._read_generic(addr, 1)

    def _read_32(self, addr):
        if (self.tar & 0xFFFFFFF0) == (addr & 0xFFFFFFF0):
            return self._read_bd((addr & 0xF) // 4)
        return self._read_generic(addr, 2)

    def _read_mem_page(self, addr, n):
        if not n:
            return

        assert (addr & 0xFFFFFC00) == ((addr + n - 1) & 0xFFFFFC00)
        if self.tar != addr:
            self._write_tar(addr)

        mem = ''
        if n >= 1 and (addr % 2):
            assert self.flags & MemAP.FLAG_SIZE_8
            self._write_csw(self.csw_base | (1<<4))
            v = (self._read_drw() >> 8*(addr % 4))
            mem  += chr((v >> 0) & 0xFF)
            addr += 1
            n    -= 1

        if n >= 2 and (addr % 4):
            assert self.flags & MemAP.FLAG_SIZE_16
            self._write_csw(self.csw_base | (1<<4) | 1)
            v = (self._read_drw() >> 8*(addr % 4))
            mem  += chr((v >> 0) & 0xFF)
            mem  += chr((v >> 8) & 0xFF)
            addr += 2
            n    -= 2

        if n >= 4:
            assert (addr % 4) == 0
            assert self.flags & MemAP.FLAG_SIZE_32
            self._write_csw(self.csw_base | (1<<4) | 2)
            while n >= 4:
                v = (self._read_drw() >> 8*(addr % 4))
                mem  += chr((v >>  0) & 0xFF)
                mem  += chr((v >>  8) & 0xFF)
                mem  += chr((v >> 16) & 0xFF)
                mem  += chr((v >> 24) & 0xFF)
                addr += 4
                n    -= 4

        if n >= 2:
            assert (addr % 2) == 0
            assert self.flags & MemAP.FLAG_SIZE_16
            self._write_csw(self.csw_base | (1<<4) | 1)
            v = (self._read_drw() >> 8*(addr % 4))
            mem  += chr((v >> 0) & 0xFF)
            mem  += chr((v >> 8) & 0xFF)
            addr += 2
            n    -= 2

        if n == 1:
            assert self.flags & MemAP.FLAG_SIZE_8
            self._write_csw(self.csw_base | (1<<4))
            v = (self._read_drw() >> 8*(addr % 4))
            mem  += chr((v >> 0) & 0xFF)
            addr += 1
            n    -= 1

        self._write_csw(self.csw_base | 2)
        self._write_tar(addr)
        return mem

    def _read_bulk(self, addr, n):
        mem = ''
        while n:
            count = min(n, 0x400 - (addr & 0x3FF))
            mem  += self._read_mem_page(addr, count)
            addr += count
            n    -= count
        return mem

    def _write_generic(self, v, addr, size):
        flag = MemAP.SIZE_TABLE[size]
        assert self.flags & flag
        if self.csw_size != size:
            self._write_csw(self.csw_base | size)
        if self.tar != addr:
            self._write_tar(addr)
        v = ((v & MemAP.MASK_TABLE[size]) << 8*(addr % 4))
        self._write_drw(v)
        if self.csw_ainc == 1:
            self.tar += (1 << size)

    def _write_8(self, v, addr):
        self._write_generic(v, addr, 0)

    def _write_16(self, v, addr):
        self._write_generic(v, addr, 1)

    def _write_32(self, v, addr):
        if (self.tar & 0xFFFFFFF0) == (addr & 0xFFFFFFF0):
            self._write_bd(v, (addr & 0xF) // 4)
        else:
            self._write_generic(v, addr, 2)

    def _write_mem_page(self, data, addr):
        if not data:
            return

        n = len(data)
        assert (addr & 0xFFFFFC00) == ((addr + n - 1) & 0xFFFFFC00)
        if self.tar != addr:
            self._write_tar(addr)

        offset = 0

        if n >= 1 and (addr % 2):
            assert self.flags & MemAP.FLAG_SIZE_8
            self._write_csw(self.csw_base | (1<<4))
            self._write_drw(struct.unpack_from('B', data, offset)[0] <<
                            8*(addr % 4))
            addr   += 1
            offset += 1
            n      -= 1

        if n >= 2 and (addr % 4):
            assert self.flags & MemAP.FLAG_SIZE_16
            self._write_csw(self.csw_base | (1<<4) | 1)
            self._write_drw(struct.unpack_from('<H', data, offset)[0] <<
                            8*(addr % 4))
            addr   += 2
            offset += 2
            n      -= 2

        if n >= 4:
            assert (addr % 4) == 0
            assert self.flags & MemAP.FLAG_SIZE_32
            self._write_csw(self.csw_base | (1<<4) | 2)
            while n >= 4:
                self._write_drw(struct.unpack_from('<I', data, offset)[0])
                addr   += 4
                offset += 4
                n      -= 4

        if n >= 2:
            assert (addr % 2) == 0
            assert self.flags & MemAP.FLAG_SIZE_16
            self._write_csw(self.csw_base | (1<<4) | 1)
            self._write_drw(struct.unpack_from('<H', data, offset)[0] <<
                            8*(addr % 4))
            addr   += 2
            offset += 2
            n      -= 2

        if n == 1:
            assert self.flags & MemAP.FLAG_SIZE_8
            self._write_csw(self.csw_base | (1<<4))
            self._write_drw(struct.unpack_from('B', data, offset)[0] <<
                            8*(addr % 4))
            addr   += 1
            offset += 1
            n      -= 1

        self._write_csw(self.csw_base | 2)
        if addr & 0x3FF:
            self.tar = addr
        else:
            self._write_tar(addr)

    def _write_bulk(self, data, addr):
        offset = 0
        n      = len(data)
        while n:
            count = min(n, 0x400 - (addr & 0x3FF))
            self._write_mem_page(data[offset:offset + count], addr)

            addr   += count
            offset += count
            n      -= count


class AHBAP(MemAP):
    '''
    AHBAP is a specific type of MEM AP and it has a different CSW register from
    other MEM APs.  We need to configure the CSW register properly to be able
    to access memory through the AP otherwise we get fault errors.
    '''
    def __init__(self, db, ap_num, idr, csw_base):
        super(AHBAP, self).__init__(db, ap_num, idr, csw_base, 'AHB')


class APBAP(MemAP):
    '''
    APBAP has DbgSwEnable in the upper bit that we need to preserve as set so
    that the CPU can continue to access debug components via the APB mux.
    '''
    def __init__(self, db, ap_num, idr, csw_base):
        super(APBAP, self).__init__(db, ap_num, idr, csw_base, 'APB')


class IDRMapper(object):
    PROBE_SIZES = (1<<0)

    def __init__(self, idr, mask, factory, csw_base, flags):
        self.idr      = idr
        self.mask     = mask
        self.factory  = factory
        self.csw_base = csw_base
        self.flags    = flags

    def probe(self, idr, db, ap_num):
        if (idr & self.mask) != self.idr:
            return None

        ap = self.factory(db, ap_num, idr, self.csw_base)
        if self.flags & IDRMapper.PROBE_SIZES:
            ap._probe_sizes()
        return ap


IDR_MAPPERS = [
    IDRMapper(0x04770001, 0x0FFFE00F, AHBAP, 0x23000040, IDRMapper.PROBE_SIZES),
    IDRMapper(0x04770002, 0x0FFFE00F, APBAP, 0x80000040, IDRMapper.PROBE_SIZES),
    IDRMapper(0x00010000, 0x0001E000, MemAP, None,       0),
    IDRMapper(0x00000000, 0x00000000, AP,    None,       0),
    ]


def probe_ap(db, ap_num, verbose=False):
    try:
        idr = db.read_ap_reg(ap_num, 0xFC)
        if idr == 0:
            return None
    except Exception:
        return None

    for im in IDR_MAPPERS:
        ap = im.probe(idr, db, ap_num)
        if not ap:
            continue

        if verbose:
            print('  Found %s with IDR 0x%08X (BASE 0x%08X)' % (
                    ap, idr, ap._read_base()))
        return ap

    if verbose:
        print('  Unhandled IDR 0x%08X' % idr)
    return None
