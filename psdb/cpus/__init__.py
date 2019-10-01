# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb.component
from . import cortex
from . import cortex_m4


# It's common practice for third-party vendors to put their own identifying
# information in the top-level Cortex ROM Table.  It's implied that this is
# normal in the Cortex-M4 spec.
psdb.component.StaticMatcher(cortex_m4.CortexM4, 0, 0xE00FF000, 0xB105100D,
                             0x000000000B1979AF,
                             subtype='MSP432P401R Cortex-M4')

# Matcher for the Cortex System Control Block.  This is matched in order to
# enable DEMCR.TRCENA so that child tables can be probed properly.  It's also
# used to do things like halt the CPU and access its registers.
psdb.component.Matcher(cortex.SystemControlBlock, 0xB105E00D,
                       0x00000004000BB000, subtype='SCB (No FPU)')
psdb.component.Matcher(cortex.SystemControlBlock, 0xB105E00D,
                       0x00000004000BB00C, subtype='SCB (With FPU)')
