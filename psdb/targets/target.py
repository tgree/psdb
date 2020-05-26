# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb

import collections
import time


class MemRegion(object):
    def __init__(self, addrs, length):
        self.addrs = addrs
        self.len   = length


class Target(object):
    def __init__(self, db, max_tck_freq):
        self.db           = db
        self.max_tck_freq = max_tck_freq
        self.cpus         = self.db.cpus
        self.devs         = collections.OrderedDict()

    def set_max_tck_freq(self):
        '''
        Sets the debug probe to the target's maximum supported SWD frequency.
        Note that this frequency may need to be throttled under some conditions
        such as during flash writes.
        '''
        return self.db.set_tck_freq(self.max_tck_freq)

    def is_halted(self, cpus=None):
        cpus = cpus or self.cpus
        for c in cpus:
            if not c.is_halted():
                return False
        return True

    def halt(self, cpus=None):
        cpus = cpus or self.cpus
        for c in cpus:
            c.halt()

    def reset_halt(self):
        '''
        This resets and then halts all of the CPUs in the system.  The way the
        STM32H7 dual-processor system works is that the AIRCR.SYSRESETREQ will
        trigger an external reset that resets all CPUs in the system rather
        than just the single CPU that requested the reset - so there is no way
        to individually reset a single CPU (unless... maybe VECTRESET can do
        this?).  It isn't clear if this is an ARM specification or if it is an
        ST implementation choice.

        To be extra rigorous, we follow this procedure:

            1. Halt all CPUs and enable reset vector catches.
            2. For each CPU, we then trigger a local reset and then wait for
               all CPUs to return to the halted state before proceeding to the
               next CPU.
            3. Disable reset vector catches.

        This should handle both cases (where SYSRESETREQ is local or global).
        '''
        # Enable reset vector catch and halt all CPUs.
        for c in self.cpus:
            c.halt()
            c.enable_reset_vector_catch()

        # Trigger a reset on all CPUs, waiting for all CPUs to halt before
        # continuing on to the next one.  This ensures that we don't trigger
        # resets while other CPUs are still handling the previous reset.
        for c in self.cpus:
            c.trigger_local_reset()
            c.wait_local_reset_complete()
            for c2 in self.cpus:
                c2.inval_halted_state()
                while not c2.is_halted():
                    pass

        # Disable reset vector catch.
        for c in self.cpus:
            c.disable_reset_vector_catch()

    def resume(self, cpus=None):
        cpus = cpus or self.cpus
        for c in cpus:
            c.resume()

    def wait_reset_and_reprobe(self, **kwargs):
        # Wait for the initial disconnect.
        try:
            while True:
                self.cpus[0].scs.read_cpuid()
                time.sleep(0.1)
        except psdb.ProbeException:
            time.sleep(0.1)

        return self.reprobe(**kwargs)

    def reprobe(self, **kwargs):
        assert self.is_halted()

        # Reprobe until we succeed.
        while True:
            try:
                t = self.db.probe(**kwargs)
                assert type(t) == type(self)
                assert t.is_halted()
                return t
            except psdb.ProbeException:
                time.sleep(0.1)
