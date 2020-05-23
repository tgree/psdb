# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb.component
from . import cortex
from . import cortex_m0p
from . import cortex_m4
from . import cortex_m7
from . import scs_v6_m
from . import scs_v7_m
from . import bpu
from . import fpb


# Cortex-M7 as defined in the ARM spec.
psdb.component.Matcher(cortex_m7.CortexM7, 0xB105100D, 0x00000004000BB4C8,
                       subtype='Cortex-M7')

# It's common practice for third-party vendors to put their own identifying
# information in the top-level Cortex ROM Table.  It's implied that this is
# normal in the Cortex-M4 spec, although the Cortex-M7 spec is silent about it.
psdb.component.StaticMatcher(cortex_m4.CortexM4, 0, 0xE00FF000, 0xB105100D,
                             0x000000000B1979AF,
                             subtype='MSP432P401R Cortex-M4')
psdb.component.StaticMatcher(cortex_m0p.CortexM0P, 0, 0xF0000000, 0xB105100D,
                             0x00000000000A0460, subtype='STM32G0 Cortex-M0+')
psdb.component.StaticMatcher(cortex_m4.CortexM4, 0, 0xE00FF000, 0xB105100D,
                             0x00000000000A0468, subtype='STM32G4 Cortex-M4')
psdb.component.StaticMatcher(cortex_m4.CortexM4, 0, 0xE00FF000, 0xB105100D,
                             0x00000000000A0469, subtype='STM32G4 Cortex-M4')
psdb.component.StaticMatcher(cortex_m4.CortexM4, 0, 0xE00FF000, 0xB105100D,
                             0x00000000000A0479, subtype='STM32G4 Cortex-M4')
psdb.component.StaticMatcher(cortex_m7.CortexM7, 0, 0xE00FE000, 0xB105100D,
                             0x00000000000A0450, subtype='STM32H7 Cortex-M7')
psdb.component.StaticMatcher(cortex_m4.CortexM4, 3, 0xE00FF000, 0xB105100D,
                             0x00000000000A0450, subtype='STM32H7 Cortex-M4')
psdb.component.StaticMatcher(cortex_m4.CortexM4, 0, 0xE00FF000, 0xB105100D,
                             0x00000000000A0495, subtype='STM32WB55 Cortex-M4')

# Matcher for the Cortex System Control Block.  This is matched in order to
# enable DEMCR.TRCENA so that child tables can be probed properly.  It's also
# used to do things like halt the CPU and access its registers.
psdb.component.Matcher(scs_v6_m.SCS, 0xB105E00D, 0x00000004000BB008,
                       subtype='SCB V6-M (No FPU)')
psdb.component.Matcher(scs_v7_m.SCS, 0xB105E00D, 0x00000004000BB000,
                       subtype='SCB V7-M (No FPU)')
psdb.component.Matcher(scs_v7_m.SCS, 0xB105E00D, 0x00000004000BB00C,
                       subtype='SCB V7-M (With FPU)')

# Matcher for the Flash Patch and Breakpoint unit.
psdb.component.Matcher(bpu.BPU, 0xB105E00D, 0x00000004000BB00B,
                       subtype='BPU (M0+)')
psdb.component.Matcher(fpb.FPB, 0xB105E00D, 0x00000004002BB003,
                       subtype='FPB (M4)')
psdb.component.Matcher(fpb.FPB, 0xB105E00D, 0x00000004000BB00E,
                       subtype='FPB (M7)')
