# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
'''
Driver for the STM32WB55 BLE Wireless Firmware.

The wireless firmware is poorly documented, to say the least.  It is a
signed, secure image distributed by ST.  You talk to it using shared memory
in SRAM2a and the IPCC control channels.  You install the firmware using a
secure firmware updater.  It's really a mess.  Here are various reference
documents that I've found to be useful:

 AN5289 - Annexes
     The annexes detail the flow of operations that need to happen to start
     up the communication channel with CPU2 and then start CPU2.  It is all
     detailed in terms of high-level calls to other ST-supplied libraries,
     so it doesn't give the details of things like what data structures
     look like.  But the sequence of operations is helpful.

 AN5185 - FUS
     This document describes the firmware upgrade services (FUS) used in the
     MCU.  The FUS is what you have to talk to in order to update the secure
     firmware for CPU2.  It also happens to detail some of the data
     structures that we need to use to talk to CPU2 (yay!).

 AN5270 - BLE Wireless Interface
     This actually documents all of the commands that you can send to the
     wireless firmware.  It doesn't document *how* to send them, mind you,
     but it's a start.

 git@github.com:STMicroelectronics/STM32CubeWB.git
     This repository contains all the ST user-level source code and examples
     for working with the wireless firmware.  In particular, the TL mailbox
     interface is all implemented under:
         Middlewares/ST/STM32_WPAN/interface/patterns/ble_thread

     The low-level IPCC stuff is under:
         Drivers/STM32WBxx_HAL_Driver/Inc/stm32wbxx_ll_ipcc.h

     And the HW_IPCC stuff is defined in each project, i.e.:
         Projects/NUCLEO-WB35CE/Applications/BLE/BLE_HeartRate/STM32_WPAN/
             Target/hw_ipcc.c

A lot of pain went into all this.  The summary for how to get in and out of
FUS is basically:

1. To get into FUS mode, you must issue FUS_GET_STATE twice.  This changes
   something in the flash so that every time the MCU boots, it will now boot
   into FUS and *not* into the wireless stack!  This change is permanent until
   you issue FUS_START_WS.

2. To get the wireless stack running again, you must issue FUS_START_WS.  This
   will change whatever is in the flash back over and the MCU will boot into
   the wireless stack instead of FUS.
'''
from .ipc import IPC


__all__ = ['IPC']
