# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import time
import struct
import hashlib
import os

import psdb
from .mailbox import Mailbox
from .system_channel import SystemChannel
from . import binaries


SYSTEM_CMD_RSP_CHANNEL  = 2
SYSTEM_EVENT_CHANNEL    = 2

EVT_PAYLOAD_WS_RUNNING  = b'\x00'
EVT_PAYLOAD_FUS_RUNNING = b'\x01'


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


    def _print_fus_version(self):
        version = self.mailbox.get_fus_version()
        print('FUS version: 0x%08X (%u.%u.%u)' % (version,
                                                  ((version >> 24) & 0xFF),
                                                  ((version >> 16) & 0xFF),
                                                  ((version >>  8) & 0xFF)))
        version = self.mailbox.get_ws_version()
        print(' WS version: 0x%08X (%u.%u.%u)' % (version,
                                                  ((version >> 24) & 0xFF),
                                                  ((version >> 16) & 0xFF),
                                                  ((version >>  8) & 0xFF)))

    def _configure_sram_boot(self):
        t = self.target

        # Write an infinite loop out of the reset handler vector.
        sp   = self.vtor_addr + 512
        pc   = (self.vtor_addr + 8) | 1
        vtor = struct.pack('<LLH', sp, pc, 0xE7FE)
        self.ap.write_bulk(vtor, self.vtor_addr)

        # Configure to boot from SRAM1 and reset.
        if not t.flash.is_sram_boot_enabled():
            initial_optr = t.flash.get_optr()
            optr = t.flash.set_boot_sram1(verbose=True)
            print('OPTR change from 0x%08X to 0x%08X' % (initial_optr, optr))
            t = t.flash.trigger_obl_launch(connect_under_reset=True)

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
                assert events[0].subevtcode == 0x9200
                if args:
                    assert events[0].payload in args
                if events[0].payload == EVT_PAYLOAD_FUS_RUNNING:
                    assert t.ipc.mailbox.check_dit_key_fus()
                elif events[0].payload == EVT_PAYLOAD_WS_RUNNING:
                    assert not t.ipc.mailbox.check_dit_key_fus()
                return t, events
            except psdb.ProbeException:
                print('Reset detected, re-probing...')
                time.sleep(0.1)
                t = t.reprobe()

    def _upgrade_firmware(self, data, fb):
        t = self.target

        assert t.ipc.mailbox.check_dit_key_fus()
        assert t.ipc.mailbox.get_ws_version() == 0
        assert hashlib.md5(data).hexdigest() == fb.md5sum
        assert len(data) % 4 == 0

        if len(data) % 8 == 4:
            data += b'\x00\x00\x00\x00'

        print('Erasing flash...')
        addr = fb.addr[t.flash.flash_size]
        t.flash.burn_dv([(addr, data)])

        print('Executing FUS_FW_UPGRADE...')
        try:
            r = t.ipc.system_channel.exec_fw_upgrade()
            print('FUS_FW_UPGRADE: %s' % r)
            assert r.status == 0x00
        except psdb.ProbeException:
            time.sleep(0.1)
            t, events = t.ipc._start_firmware(EVT_PAYLOAD_FUS_RUNNING)

        while True:
            try:
                r = t.ipc.system_channel.exec_get_state()
                print('FUS_GET_STATE: %s' % r)
                assert r.status != 0xFF
                if r.status == 0x00:
                    print('Finished in FUS mode.')
                    t.ipc._print_fus_version()
                    return t
                time.sleep(0.1)
            except psdb.ProbeException:
                time.sleep(0.1)
                t, events = t.ipc._start_firmware()
                if events[0].payload == EVT_PAYLOAD_WS_RUNNING:
                    print('Finished in WS firmware mode.')
                    return t

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

    def start_fus_firmware(self):
        '''
        Start CPU2 up in FUS mode.  The sequence is convoluted and may
        involve multiple reboots, which invalidates the debugger connection
        and target object.

        This method returns a new psdb.target object and the old object must be
        discarded since it is no longer valid after the reset.  The correct
        idiom for use is:

            target = target.ipc.start_fus_firmware()
        '''
        t = self.target

        print('0. Configuring SRAM booting...')
        t = t.ipc._configure_sram_boot()

        print('1. Starting firmware and waiting for first event...')
        t, events = t.ipc._start_firmware()
        if (events[0].payload == EVT_PAYLOAD_FUS_RUNNING and
                t.ipc.mailbox.check_dit_key_fus()):
            t.ipc._print_fus_version()
            r = t.ipc.system_channel.exec_get_state()
            print('Already in FUS mode, FUS_GET_STATE: %s' % r)
            return t

        print('Not in FUS mode.')
        print('2. Executing first FUS_GET_STATE...')
        r = t.ipc.system_channel.exec_get_state()
        if r.status != 0xFF:
            r.dump()
            raise Exception('Unexpected FUS status 0x%02X' % r.status)

        print('3. Executing second FUS_GET_STATE...')
        t.ipc.system_channel._start_get_state()

        print('4. Waiting for reset and reprobing...')
        t = t.wait_reset_and_reprobe()

        print('5. Starting firmware and waiting up to 5 seconds for reset...')
        t, events = t.ipc._start_firmware(EVT_PAYLOAD_FUS_RUNNING)
        t.ipc._print_fus_version()

        return t

    def upgrade_fus_firmware(self, bin_dir):
        '''
        Upgrades to the latest FUS firmware.  The following images must be
        present in the bin_dir directory:

            stm32wb5x_FUS_fw_1_0_2.bin - 1.0.2 FUS binary
            stm32wb5x_FUS_fw.bin       - 1.1.0 FUS binary

        The FUS firmware should already have been started via
        start_fus_firmware().
        '''
        t = self.target

        assert t.ipc.mailbox.check_dit_key_fus()
        assert t.ipc.mailbox.get_ws_version() == 0

        version = (t.ipc.mailbox.get_fus_version() & 0xFFFFFF00)
        if version == binaries.FUS_BINARY_LATEST.version:
            print('FUS already at latest version %s.'
                  % binaries.FUS_BINARY_LATEST.version_str)
            return t
        elif version == 0x00050300:
            fb = binaries.find_fus_binary(0x01000200)
        elif version == 0x01000200:
            fb = binaries.find_fus_binary(0x01010000)
        else:
            raise Exception("Don't know how to upgrade from 0x%08X" % version)

        print('Upgrading to %s' % fb.version_str)
        bin_path = os.path.join(bin_dir, fb.fname)
        with open(bin_path, 'rb') as f:
            data = f.read()

        return self._upgrade_firmware(data, fb)

    def start_ws_firmware(self):
        '''
        Start CPU2 in wireless firmware mode.  The sequence is fairly
        straightforward:

            1. Connect under reste.
        will switch it over to firmware mode and then it will reboot.  We'll
        have to reset it again to halt it at the reset vector.  It's an ugly
        procedure.

        This method returns a new psdb.target object and the old object must be
        discarded since it is no longer valid after the reset.  The correct
        idiom for use of fw_enter is:

            target = target.ipc.fw_enter()
        '''
        t = self.target

        t = t.ipc._configure_sram_boot()

        t, events = t.ipc._start_firmware()
        if events[0].payload == EVT_PAYLOAD_WS_RUNNING:
            return t
        assert t.ipc.mailbox.get_ws_version() != 0

        t.ipc.system_channel._start_start_ws()
        t = t.wait_reset_and_reprobe()

        t, events = t.ipc._start_firmware(EVT_PAYLOAD_WS_RUNNING)

        return t

    def delete_ws_firmware(self):
        '''
        Delete the wireless firmware.  The sequence is:

            1. Enter FUS firwmare mode via start_fus_firmware().
            2. Start FUS_FW_DELETE - a device reset is expected.
            3. Reprobe not under reset.
            4. Start firwmare and wait for first event.
               - if event is 'FUS running' and FUS key found, done
               - otherwise, panic.

        This method returns a new psdb.target object and the old object must be
        discarded since it is no longer valid after the reset.  The correct
        idiom for use is:

            target = target.ipc.delete_ws_firmware()
        '''
        t = self.target

        assert t.ipc.mailbox.check_dit_key_fus()
        assert t.ipc.mailbox.get_ws_version() != 0

        try:
            r = t.ipc.system_channel.exec_fw_delete()
            print('FUS_FW_DELETE: %s' % r)
            assert r.status == 0x00
        except psdb.ProbeException:
            time.sleep(0.1)
            t, events = t.ipc._start_firmware(EVT_PAYLOAD_FUS_RUNNING)

        while True:
            try:
                r = t.ipc.system_channel.exec_get_state()
                print('FUS_GET_STATE: %s' % r)
                assert r.status != 0xFF
                if r.status == 0x00:
                    break
                time.sleep(0.1)
            except psdb.ProbeException:
                time.sleep(0.1)
                t, events = t.ipc._start_firmware(EVT_PAYLOAD_FUS_RUNNING)

        assert t.ipc.mailbox.get_ws_version() == 0

        return t

    def upgrade_ws_firmware(self, bin_path):
        assert self.mailbox.check_dit_key_fus()
        assert self.mailbox.get_ws_version() == 0

        with open(bin_path, 'rb') as f:
            data = f.read()
        md5sum = hashlib.md5(data).hexdigest()
        fb     = binaries.find_ws_binary(md5sum)

        return self._upgrade_firmware(data, fb)
