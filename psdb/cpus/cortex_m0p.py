# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from . import cortex


class CortexM0P(cortex.Cortex):
    def __init__(self, component, subtype):
        super().__init__(component, subtype, 'M0+')
