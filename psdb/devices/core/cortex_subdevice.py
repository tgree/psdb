# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from psdb.devices import Device
from psdb.component import Component
from psdb.cpus.cortex import Cortex


class CortexSubDevice(Device, Component):
    def __init__(self, name, regs, component, subtype):
        cortex_cpu, = component.find_by_type_towards_root(Cortex)
        path        = ('CPU%u:%s' % (cortex_cpu.cpu_index, name))

        Device.__init__(self, cortex_cpu, component.ap, component.addr, name,
                        regs, path=path)
        Component.__init__(self, component.parent, component.ap, component.addr,
                           subtype)
