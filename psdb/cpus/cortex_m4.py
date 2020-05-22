# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from . import cortex
from ..targets import scs_v7_m


class CortexM4(cortex.Cortex):
    def __init__(self, component, subtype):
        super(CortexM4, self).__init__(component, subtype)

    def make_scs(self, target, index):
        return scs_v7_m.SCS(target, self.scb.ap, 'SCS%u' % index, self.scb.addr)
