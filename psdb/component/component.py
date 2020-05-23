# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from . import matcher


class Component(object):
    def __init__(self, parent, ap, addr, subtype=''):
        self.parent   = parent
        self.ap       = ap
        self.addr     = addr
        self.subtype  = subtype
        self.cidr     = self.read_id_block(self.addr + 0xFF0)
        self.pidr     = ((self.read_id_block(self.addr + 0xFD0) << 32) |
                         (self.read_id_block(self.addr + 0xFE0) <<  0))
        self.children = []

    def __repr__(self):
        return "Component '%s':0x%08X:0x%08X:0x%016X %s" % (
                self.ap, self.addr, self.cidr, self.pidr, self.subtype)

    @staticmethod
    def probe(ap, entry, base=0, parent=None):
        if entry == 0x00000000:
            # End of table
            return None
        if entry == 0xFFFFFFFF:
            # Legacy not-present
            return None
        if (entry & 0x00000001) == 0:
            # Not-present
            return None
        if (entry & 0x00000002) == 0:
            # Not a 32-bit ROM Table entry
            return None

        c = Component(parent, ap, (base + entry) & 0xFFFFF000)
        return matcher.match(c)

    def probe_children(self, prefix='  ', verbose=False):
        '''
        Probe for child components.  If we've already probed for children, this
        will discard the existing children and do the hierarchy again.  This is
        useful if components are enabled/disabled on the fly.
        '''
        # Probe based on the CIDR and the PIDR.  The CIDR always has the
        # following format:
        #
        #   0xB105n00D
        #
        # The n value identifies the component class:
        #
        #   0   - generic verification component
        #   1   - ROM table
        #   2-8 - reserved
        #   9   - debug component
        #   A   - reserved
        #   B   - peripheral test block
        #   C   - reserved
        #   D   - OptimoDE Data Engine SubSystem (DESS) component
        #   E   - generic IP component
        #   F   - PrimeCell peripheral
        self.children = []
        if ((self.cidr & 0xFFFF0FFF) != 0xB105000D):
            return
        if ((self.cidr >> 12) & 0xF) != 1:
            return

        offset = 0
        while True:
            entry = self.ap.read_32(self.addr + offset)
            if entry == 0:
                break

            c = Component.probe(self.ap, entry, base=self.addr, parent=self)
            if c is not None:
                if verbose:
                    print('  %s%s' % (prefix, c))
                self.children.append(c)

            offset += 4

        prefix += '  '
        for c in self.children:
            c.probe_children(prefix=prefix, verbose=verbose)

    def read_id_block(self, addr):
        mem = self.ap.read_bulk(addr, 16)
        return (((ord(mem[12:13]) << 24) & 0xFF000000) |
                ((ord(mem[ 8: 9]) << 16) & 0x00FF0000) |
                ((ord(mem[ 4: 5]) <<  8) & 0x0000FF00) |
                ((ord(mem[ 0: 1]) <<  0) & 0x000000FF))

    def find_component(self, cidr, pidr):
        if self.cidr == cidr and self.pidr == pidr:
            return self

        for c in self.children:
            cc = c.find_component(cidr, pidr)
            if cc:
                return cc

        return None

    def _find_components_by_type(self, typ, results):
        if isinstance(self, typ):
            results.append(self)

        for c in self.children:
            c._find_components_by_type(typ, results)

    def find_components_by_type(self, typ):
        '''
        Searchs towards the leaves of the tree for components of the specified
        type.  The initial node is included for consideration in the list of
        searched components.
        '''
        results = []
        self._find_components_by_type(typ, results)
        return results

    def _find_by_type_towards_root(self, typ, results):
        if isinstance(self, typ):
            results.append(self)

        if self.parent:
            self.parent._find_by_type_towards_root(typ, results)

    def find_by_type_towards_root(self, typ):
        '''
        Searches towards the root of the tree for components of the specified
        type.  The initial node is included for consideration in the list of
        searched components.
        '''
        results = []
        self._find_by_type_towards_root(typ, results)
        return results

    def dump(self, prefix=''):
        print('%s%s' % (prefix, self))
        for c in self.children:
            assert c.parent == self
            c.dump(prefix + '  ')
