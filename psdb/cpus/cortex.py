# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb


FLAG_HALTED   = (1<<0)


class Cortex(psdb.component.Component):
    '''
    Base class component matcher for Cortex CPUs.  This is where we have common
    code for Cortex-M4 and Cortex-M7; there's no guarantee that this will work
    for any other Cortex model.
    '''
    def __init__(self, component, subtype, model):
        super(Cortex, self).__init__(component.parent, component.ap,
                                     component.addr, subtype)
        self.model     = model
        self._scs      = None
        self._bpu      = None
        self.flags     = 0
        self.cpu_index = len(self.ap.db.cpus)
        self.devs      = {}
        self.ap.db.cpus.append(self)

    @property
    def scs(self):
        if self._scs is None:
            self._scs = self.devs['SCS']
        return self._scs

    @property
    def bpu(self):
        if self._bpu is None:
            self._bpu = self.devs.get('BPU', None)
        if self._bpu is None:
            self._bpu = self.devs.get('FPB', None)
        return self._bpu

    def is_halted(self):
        '''
        Returns True if the CPU is halted, False otherwise.
        '''
        # If we haven't started it since the last time it was halted, then it's
        # still halted.
        if self.flags & FLAG_HALTED:
            return True

        # Okay, it was running last time we checked.  Check again since it may
        # have halted.
        if self.scs.is_halted():
            self.flags |= FLAG_HALTED
            return True

        # It hasn't halted, so it's still running.
        return False

    def inval_halted_state(self):
        self.flags &= ~FLAG_HALTED

    def read_8(self, addr):
        return self.ap.read_8(addr)

    def read_16(self, addr):
        return self.ap.read_16(addr)

    def read_32(self, addr):
        return self.ap.read_32(addr)

    def read_bulk(self, addr, size):
        return self.ap.read_bulk(addr, size)

    def read_core_register(self, name):
        '''Reads a single core register.'''
        assert self.flags & FLAG_HALTED
        return self.scs.read_core_register(name)

    def read_core_registers(self):
        '''Read all of the core registers.'''
        return self.scs.read_core_registers()

    def write_8(self, v, addr):
        self.ap.write_8(v, addr)

    def write_16(self, v, addr):
        self.ap.write_16(v, addr)

    def write_32(self, v, addr):
        self.ap.write_32(v, addr)

    def write_bulk(self, data, addr):
        self.ap.write_bulk(data, addr)

    def write_demcr(self, v):
        return self.ap.write_32(v, self.scs.addr + 0xDFC)

    def write_core_register(self, v, name):
        '''Writes a single core register.'''
        self.scs.write_core_register(v, name)

    def halt(self):
        '''Halts the CPU.'''
        if self.flags & FLAG_HALTED:
            return

        self.scs.halt()
        self.flags |= FLAG_HALTED

    def single_step(self):
        '''Steps the CPU for a single instruction.'''
        assert self.flags & FLAG_HALTED
        self.scs.single_step()

    def resume(self):
        '''Resumes execution of a halted CPU.'''
        if not (self.flags & FLAG_HALTED):
            return

        self.scs.resume()
        self.flags &= ~FLAG_HALTED

    def enable_reset_vector_catch(self):
        self.scs.enable_reset_vector_catch()

    def disable_reset_vector_catch(self):
        self.scs.disable_reset_vector_catch()

    def trigger_local_reset(self):
        self.scs.trigger_aircr_local_reset()
        self.wait_local_reset_complete()

    def wait_local_reset_complete(self):
        self.scs.wait_aircr_local_reset_complete()
        self.flags &= ~FLAG_HALTED
