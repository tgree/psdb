# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import time
import struct

import psdb
from .mailbox import Mailbox
from .system_channel import (SystemChannel,
                             SHCI_SUBEVTCODE_READY,
                             EVT_PAYLOAD_WS_RUNNING,
                             EVT_PAYLOAD_FUS_RUNNING,
                             )
from .mm_channel import MMChannel
from .ble_channel import BLEChannel
from .fus_client import FUSClient
from . import ws_factory


BLE_CMD_CHANNEL         = 1
BLE_EVENT_CHANNEL       = 1
SYSTEM_CMD_RSP_CHANNEL  = 2
SYSTEM_EVENT_CHANNEL    = 2
MM_CMD_CHANNEL          = 4


class IPC(object):
    def __init__(self, target, ap, base_addr, ram_size, vtor_addr):
        super(IPC, self).__init__()
        self.target    = target
        self.ap        = ap
        self.base_addr = base_addr
        self.ram_size  = ram_size
        self.vtor_addr = vtor_addr
        self.ipcc      = self.target.devs['IPCC']
        self.rcc       = self.target.devs['RCC']
        self.pwr       = self.target.devs['PWR']

        self.mailbox        = Mailbox(ap, base_addr, ram_size)
        self.system_channel = SystemChannel(self, SYSTEM_CMD_RSP_CHANNEL,
                                            SYSTEM_EVENT_CHANNEL)
        self.mm_channel     = MMChannel(self, MM_CMD_CHANNEL)
        self.ble_channel    = BLEChannel(self, BLE_CMD_CHANNEL,
                                         BLE_EVENT_CHANNEL)

    def set_tx_flag(self, channel):
        self.ipcc.set_tx_flag(channel)

    def is_tx_free(self, channel):
        return self.ipcc.get_tx_free_flag(channel)

    def wait_tx_free(self, channel, timeout=None):
        self.ipcc.wait_tx_free(channel, timeout=timeout)

    def get_rx_flag(self, channel):
        return self.ipcc.get_rx_flag(channel)

    def wait_rx_occupied(self, channel, timeout=None):
        self.ipcc.wait_rx_occupied(channel, timeout=timeout)

    def clear_rx_flag(self, channel):
        self.ipcc.clear_rx_flag(channel)

    def _configure_sram_boot(self):
        t = self.target

        # Write an infinite loop out of the reset handler vector.
        sp   = self.vtor_addr + 512
        pc   = (self.vtor_addr + 8) | 1
        vtor = struct.pack('<LLH', sp, pc, 0xE7FE)
        self.ap.write_bulk(vtor, self.vtor_addr)

        # Configure to boot from SRAM1 and reset.
        if not t.flash.is_sram_boot_enabled():
            t = t.flash.set_boot_sram1(verbose=True,
                                       connect_under_reset=True)

        return t

    def _start_firmware(self, *args):
        t = self.target

        while True:
            try:
                assert not t.ipc.pwr.is_cpu2_boot_enabled()

                t.ipc.mailbox.write_tables()
                t.ipc.rcc.enable_device('IPCC')
                t.ipc.pwr.enable_cpu2_boot()
                events = t.ipc.system_channel.wait_and_pop_all_events()
                assert len(events) == 1
                assert events[0].subevtcode == SHCI_SUBEVTCODE_READY
                if events[0].payload == EVT_PAYLOAD_FUS_RUNNING:
                    client = FUSClient(t.ipc)
                elif events[0].payload == EVT_PAYLOAD_WS_RUNNING:
                    client = ws_factory.make_client(
                            t.ipc, t.ipc.mailbox.read_stack_type())
                else:
                    raise Exception('Unrecognized event %s' % events[0])
                if args:
                    assert isinstance(client, args)
                return t, client
            except psdb.ProbeException:
                print('Reset detected, re-probing...')
                time.sleep(0.1)
                t = t.reprobe()

    def start_firmware(self):
        '''
        Places the target into boot-from-SRAM mode and then starts CPU2
        firmware, returning a client that knows how to communicate with
        whatever stack (FUS or BLE) starts up on CPU2.  This may entail one or
        more MCU reboots, so a new target and client instance are both
        returned.
        '''
        self._configure_sram_boot()
        return self._start_firmware()
