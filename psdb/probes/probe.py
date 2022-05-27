# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb
import psdb.targets

import time
from builtins import range
from struct import pack, unpack


class Enumeration:
    def __init__(self, cls):
        self.cls = cls

    def make_probe(self):
        raise NotImplementedError

    def show_info(self):
        raise NotImplementedError


class Probe(object):
    def __init__(self):
        self.aps    = {}
        self.cpus   = []
        self.target = None
        self.dpidr  = None

    def assert_srst(self):
        raise NotImplementedError

    def deassert_srst(self):
        raise NotImplementedError

    def set_tck_freq(self, freq):
        raise NotImplementedError

    def open_ap(self, ap_num):
        raise NotImplementedError

    def _bulk_read_8(self, addr, n, ap_num=0):
        raise NotImplementedError

    def _bulk_read_16(self, addr, n, ap_num=0):
        raise NotImplementedError

    def _bulk_read_32(self, addr, n, ap_num=0):
        raise NotImplementedError

    def _bulk_write_8(self, data, addr, ap_num=0):
        raise NotImplementedError

    def _bulk_write_16(self, data, addr, ap_num=0):
        raise NotImplementedError

    def _bulk_write_32(self, data, addr, ap_num=0):
        raise NotImplementedError

    def read_32(self, addr, ap_num=0):
        return unpack('<I', self._bulk_read_32(addr, 1, ap_num=ap_num))[0]

    def read_16(self, addr, ap_num=0):
        return unpack('<H', self._bulk_read_16(addr, 1, ap_num=ap_num))[0]

    def read_8(self, addr, ap_num=0):
        return unpack('<B', self._bulk_read_8(addr, 1, ap_num=ap_num))[0]

    def write_32(self, v, addr, ap_num=0):
        self._bulk_write_32(pack('<I', v), addr, ap_num=ap_num)

    def write_16(self, v, addr, ap_num=0):
        self._bulk_write_16(pack('<H', v), addr, ap_num=ap_num)

    def write_8(self, v, addr, ap_num=0):
        self._bulk_write_8(pack('<B', v), addr, ap_num=ap_num)

    def read_bulk(self, addr, size, ap_num=0):
        '''
        Do a bulk read operation from the specified address.  If the start or
        end addresses are not word-aligned then multiple transactions will take
        place.  If the address range crosses a 1K page boundary, multiple
        transactions will take place to handle the TAR auto-increment issue.

        Note: this helper relies on the probe implementing _bulk_read_8() and
        _bulk_read_32() methods.  The probe should override this method if it
        needs to do a different type of offload.
        '''
        # Handle empty transfers.
        if not size:
            return bytes(b'')

        # For short misaligned transfers, just do a single 8-bit access
        # transaction.
        if ((addr % 4) or (size % 4)) and size <= 64:
            return self._bulk_read_8(addr, size, ap_num)

        # For long transfers, align with 8-bit, then do 32-bit, then do 8-bit
        # for the tail.
        mem         = bytes(b'')
        align_count = (4 - addr) & 3
        count       = min(align_count, size)
        if count:
            mem  += self._bulk_read_8(addr, count, ap_num)
            addr += count
            size -= count
        while size >= 4:
            count = min(size, 0x400 - (addr & 0x3FF))//4
            mem  += self._bulk_read_32(addr, count, ap_num)
            addr += count*4
            size -= count*4
        if size:
            mem += self._bulk_read_8(addr, size, ap_num)
        return mem

    def write_bulk(self, data, addr, ap_num=0):
        '''
        Note: this helper relies on the probe implementing _bulk_write_8() and
        _bulk_write_32() methods.  The probe should override this method if it
        needs to do a different type of offload.
        '''
        # Handle empty transfers.
        if not data:
            return

        # For short misaligned transfers, just do a single 8-bit bulk
        # transaction.
        if ((addr % 4) or (len(data) % 4)) and len(data) <= 64:
            return self._bulk_write_8(data, addr, ap_num)

        # For long transfers, align with 8-bit, then do 32-bit, then do 8-bit
        # for the tail.
        align_count = (4 - addr) & 3
        count       = min(align_count, len(data))
        if count:
            self._bulk_write_8(data[:count], addr, ap_num)
            addr += count
            data  = data[count:]
        while len(data) >= 4:
            count = min(len(data), 0x400 - (addr & 0x3FF))//4
            self._bulk_write_32(data[:count*4], addr, ap_num)
            addr += count*4
            data  = data[count*4:]
        if data:
            self._bulk_write_8(data, addr, ap_num)

    def exec_cmd_list(self, cmd_list):
        read_vals = []
        for cmd in cmd_list:
            if isinstance(cmd, psdb.devices.ReadCommand):
                assert cmd.ap.db == self
                if cmd.size == 4:
                    read_vals.append(self.read_32(cmd.addr, cmd.ap.ap_num))
                elif cmd.size == 2:
                    read_vals.append(self.read_16(cmd.addr, cmd.ap.ap_num))
                elif cmd.size == 1:
                    read_vals.append(self.read_8(cmd.addr, cmd.ap.ap_num))
                else:
                    raise Exception('Illegal size %u in cmd list.' % cmd.size)
            else:
                raise Exception('Unrecognized command: %s' % cmd)
        return read_vals

    def halt(self):
        for c in self.cpus:
            c.halt()

    def _probe_dp_v1(self, verbose=False):
        '''Probe all 256 APs for a non-zero IDR.'''
        self.aps = {}
        for ap_num in range(256):
            try:
                self.open_ap(ap_num)
            except Exception:
                continue

            ap = psdb.access_port.probe_ap(self, ap_num, verbose=verbose)
            if ap:
                self.aps[ap_num] = ap

    def _probe_dp_v2(self, verbose=False):
        '''Just probe as though it were a v1 DP for now.'''
        self._probe_dp_v1(verbose=verbose)

    def probe(self, verbose=False, connect_under_reset=False):
        '''
        First discovers which APs are attached to the debug probe and then
        performs component topology detection on each AP.  Finally, we attempt
        to match the resulting components to a known target.

        After components have been matched, the target must be halted before it
        is further probed.  When we return, the target remains in the halted
        state and Target.resume() must be invoked if it is to continue running.

        If connect_under_reset is True, the SRST line will be asserted and then
        both the connection process and the component probing will take place
        while the MCU is held in SRST.  Reset vector catch will then be
        configured, SRST will be released and the MCU will then end up halted
        right in the reset vector and we return.

        If connect_under_reset is False, the SRST line will be deasserted (in
        case it had been previously asserted - we assume that the MCU does not
        support probing under SRST) and then component probing will take place
        *while the MCU is running*.  Finally, the MCU will be halted wherever
        it happens to be running and we return.
        '''
        if connect_under_reset:
            self.assert_srst()
        else:
            self.deassert_srst()

        self.connect()

        dpver = ((self.dpidr & 0x0000F000) >> 12)
        if dpver == 1:
            self._probe_dp_v1(verbose=verbose)
        elif dpver == 2:
            self._probe_dp_v2(verbose=verbose)
        else:
            raise psdb.ProbeException('Unsupported DP version %u (0x%08X)' % (
                                      dpver, self.dpidr))

        psdb.targets.pre_probe(self, verbose)

        self.cpus = []
        for _, ap in self.aps.items():
            if hasattr(ap, 'probe_components'):
                ap.base_component = ap.probe_components(verbose=verbose)

        if connect_under_reset:
            for c in self.cpus:
                c.enable_reset_vector_catch()

            self.deassert_srst()

            for c in self.cpus:
                c.inval_halted_state()
                while not c.is_halted():
                    pass

            for c in self.cpus:
                c.disable_reset_vector_catch()
        else:
            self.halt()

        self.target = psdb.targets.probe(self)
        assert self.target

        if verbose:
            print('  Identified target %s' % self.target)

        return self.target

    def srst_target(self):
        self.assert_srst()
        time.sleep(0.00001)
        self.deassert_srst()
        time.sleep(0.001)
