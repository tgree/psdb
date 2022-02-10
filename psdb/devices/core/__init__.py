# Copyright (c) 2019-2020 Phase Advanced Sensor Systems, Inc.
import psdb.component
from . import bpu
from . import fpb
from . import scs_v6_m
from . import scs_v7_m
from . import scs_v8_m
from . import dwt_m4
from . import itm_m4
from . import tpiu_m4


# Matcher for the Cortex System Control Block.  This is matched in order to
# enable DEMCR.TRCENA so that child tables can be probed properly.  It's also
# used to do things like halt the CPU and access its registers.
psdb.component.Matcher(scs_v6_m.SCS, 0xB105E00D, 0x00000004000BB008,
                       subtype='SCB V6-M (No FPU)')
psdb.component.Matcher(scs_v7_m.SCS, 0xB105E00D, 0x00000004000BB000,
                       subtype='SCB V7-M (No FPU)')
psdb.component.Matcher(scs_v7_m.SCS, 0xB105E00D, 0x00000004000BB00C,
                       subtype='SCB V7-M (With FPU)')
psdb.component.M33Matcher(scs_v8_m.SCS, 0xE000E000, 0xB105900D,
                          0x00000004000BBD21, 0x47702A04, 0x00000000,
                          subtype='SCB V8-M')

# Matcher for the Data Watchpoint and Trace (DWT) unit.
psdb.component.Matcher(dwt_m4.DWT, 0xB105E00D, 0x00000004003BB002,
                       subtype='DWT (M4)')

# Matcher for the Instrumentation Trace Macrocell (ITM) unit.
psdb.component.Matcher(itm_m4.ITM, 0xB105E00D, 0x00000004003BB001,
                       subtype='ITM (M4)')

# Matcher for the Trace Port Interface Unit (TPIU).
psdb.component.Matcher(tpiu_m4.TPIU, 0xB105900D, 0x00000004000BB9A1,
                       subtype='TPIU (M4)')

# Matcher for the Flash Patch and Breakpoint unit.
psdb.component.Matcher(bpu.BPU, 0xB105E00D, 0x00000004000BB00B,
                       subtype='BPU (M0+)')
psdb.component.Matcher(fpb.FPB, 0xB105E00D, 0x00000004002BB003,
                       subtype='FPB (M4)')
psdb.component.Matcher(fpb.FPB, 0xB105E00D, 0x00000004000BB00E,
                       subtype='FPB (M7)')
