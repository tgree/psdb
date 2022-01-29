# Copyright (c) 2021 by Phase Advanced Sensor Systems, Inc.
from . import cortex


class CortexM33(cortex.Cortex):
    def __init__(self, component, subtype):
        super().__init__(component, subtype, 'M33')
