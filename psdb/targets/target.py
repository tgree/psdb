# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import collections


class MemRegion(object):
    def __init__(self, addrs, length):
        self.addrs = addrs
        self.len   = length


class Target(object):
    def __init__(self, db):
        self.db   = db
        self.cpus = self.db.cpus
        self.devs = collections.OrderedDict()

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

    def reset_halt(self, cpus=None):
        cpus = cpus or self.cpus
        for c in cpus:
            c.reset_halt()

    def resume(self, cpus=None):
        cpus = cpus or self.cpus
        for c in cpus:
            c.resume()
