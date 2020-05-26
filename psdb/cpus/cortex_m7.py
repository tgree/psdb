# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from . import cortex


class CortexM7(cortex.Cortex):
    def __init__(self, component, subtype):
        super(CortexM7, self).__init__(component, subtype, 'M7')
