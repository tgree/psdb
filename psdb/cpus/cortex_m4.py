# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from . import cortex


class CortexM4(cortex.Cortex):
    def __init__(self, component, subtype):
        super(CortexM4, self).__init__(component, subtype, 'M4')
