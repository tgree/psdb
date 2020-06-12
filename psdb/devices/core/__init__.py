# Copyright (c) 2019-2020 Phase Advanced Sensor Systems, Inc.
import psdb.component
from . import bpu
from . import fpb
from . import scs_v6_m
from . import scs_v7_m


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
