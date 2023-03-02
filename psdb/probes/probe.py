# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import time
from builtins import range
from struct import pack, unpack

import psdb
import psdb.targets


class Enumeration:
    def __init__(self, cls, *args, **kwargs):
        self.cls    = cls
        self.args   = args
        self.kwargs = kwargs

    def __repr__(self):
        return self.cls.NAME

    def _match_kwargs(self, **kwargs):
        return kwargs

    def make_probe(self):
        return self.cls(*self.args, **self.kwargs)

    def show_info(self):
        return self.cls.show_info(*self.args, **self.kwargs)

    def match(self, **kwargs):
        return not self._match_kwargs(**kwargs)

    @staticmethod
    def filter(enumerations, **kwargs):
        return [e for e in enumerations if e.match(**kwargs)]


class Stats:
    def dump(self):
        print("Statistics not supported.")


class Probe:
    NAME = None

    def __init__(self):
        self.aps          = {}
        self.cpus         = []
        self.target       = None
        self.max_tck_freq = None

    @staticmethod
    def find():
        enumerations = []
        for cls in psdb.probes.PROBE_CLASSES:
            enumerations += cls.find()
        return enumerations

    @classmethod
    def make_one(cls, **kwargs):
        max_tck_freq = kwargs.pop('max_tck_freq', None)
        enumerations = Enumeration.filter(cls.find(), **kwargs)
        if not enumerations:
            raise psdb.ProbeException('No probe found.')
        if len(enumerations) == 1:
            p = enumerations[0].make_probe()
            p.max_tck_freq = max_tck_freq
            return p

        print('Found probes:')
        for e in enumerations:
            e.show_info()
        raise psdb.ProbeException('Multiple probes found.')

    def connect(self):
        raise NotImplementedError

    def assert_srst(self):
        raise NotImplementedError

    def deassert_srst(self):
        raise NotImplementedError

    def set_max_target_tck_freq(self):
        return self.set_tck_freq(self.target.max_tck_freq)

    def set_max_burn_tck_freq(self, _flash):
        return self.set_max_target_tck_freq()

    def set_tck_freq(self, freq_hz):
        if self.max_tck_freq is not None:
            freq_hz = min(freq_hz, self.max_tck_freq)
        return self._set_tck_freq(freq_hz)

    def _set_tck_freq(self, freq_hz):
        raise NotImplementedError

    def get_stats(self):
        '''
        Return accumulated stats since the last time get_stats was invoked.
        '''
        return Stats()

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

        mem = bytearray()

        # Align us to a 32-bit boundary.
        count = min(size, -addr & 3)
        if count:
            mem  += self._bulk_read_8(addr, count, ap_num)
            addr += count
            size -= count

        # Do 32-bit aligned transfers that don't cross TAR boundaries.
        while size >= 4:
            count = min(size, 0x400 - (addr & 0x3FF)) // 4
            mem  += self._bulk_read_32(addr, count, ap_num)
            addr += count * 4
            size -= count * 4

        # Do any remaining bytes.
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

        mv = memoryview(data)

        # Align us to a 32-bit boundary.
        count = min(len(mv), -addr & 3)
        if count:
            self._bulk_write_8(mv[:count], addr, ap_num)
            addr += count
            mv    = mv[count:]

        # Do 32-bit aligned transfers that don't cross TAR boundaries.
        while len(mv) >= 4:
            count = min(len(mv), 0x400 - (addr & 0x3FF)) // 4
            self._bulk_write_32(mv[:count * 4], addr, ap_num)
            addr += count * 4
            mv    = mv[count * 4:]

        # Do any remaining bytes.
        if mv:
            self._bulk_write_8(mv, addr, ap_num)

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

        dpidr = self.connect()

        dpver = ((dpidr & 0x0000F000) >> 12)
        if dpver == 1:
            self._probe_dp_v1(verbose=verbose)
        elif dpver == 2:
            self._probe_dp_v2(verbose=verbose)
        else:
            raise psdb.ProbeException('Unsupported DP version %u (0x%08X)' % (
                                      dpver, dpidr))

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
