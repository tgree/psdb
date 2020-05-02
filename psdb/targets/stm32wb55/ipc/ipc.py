# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import time
import struct

import psdb
from .mailbox import Mailbox
from .system_channel import SystemChannel
from .fus_client import FUSClient
from .ws_client import WSClient
from .ble_client import BLEClient


SYSTEM_CMD_RSP_CHANNEL  = 2
SYSTEM_EVENT_CHANNEL    = 2

EVT_PAYLOAD_WS_RUNNING  = b'\x00'
EVT_PAYLOAD_FUS_RUNNING = b'\x01'

WS_TYPE_BLE_STANDARD          = 0x01
WS_TYPE_BLE_HCI               = 0x02
WS_TYPE_BLE_LIGHT             = 0x03
WS_TYPE_THREAD_FTD            = 0x10
WS_TYPE_THREAD_MTD            = 0x11
WS_TYPE_ZIGBEE_FFD            = 0x30
WS_TYPE_ZIGBEE_RFD            = 0x31
WS_TYPE_MAC                   = 0x40
WS_TYPE_BLE_THREAD_FTD_STATIC = 0x50
WS_TYPE_802154_LLD_TESTS      = 0x60
WS_TYPE_802154_PHY_VALID      = 0x61
WS_TYPE_BLE_PHY_VALID         = 0x62
WS_TYPE_BLE_LLD_TESTS         = 0x63
WS_TYPE_BLE_RLV               = 0x64
WS_TYPE_802154_RLV            = 0x65
WS_TYPE_BLE_ZIGBEE_FFD_STATIC = 0x70


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

    def set_tx_flag(self, channel):
        self.ipcc.set_tx_flag(channel)

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

    def _make_client(self, stack_type):
        if stack_type == WS_TYPE_BLE_STANDARD:
            return BLEClient(self)
        raise Exception('No client for WS stack type 0x%02X' % stack_type)

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
                assert events[0].subevtcode == 0x9200
                if events[0].payload == EVT_PAYLOAD_FUS_RUNNING:
                    client = FUSClient(t.ipc)
                elif events[0].payload == EVT_PAYLOAD_WS_RUNNING:
                    client = t.ipc._make_client(t.ipc.mailbox.read_stack_type())
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
