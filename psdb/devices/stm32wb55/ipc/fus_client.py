# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
'''
FUS really does only use the system channel, system event channel and
optionally the trace channel.  It does NOT use the memory manager.  FUS
events come from the sys_spare_evt_buffer - they are not allocated out of
the memory manager pool.  Trying to post them back into the memory manager
pool just leaves the IPCC channel flag set.  There can only be one event in
use at a time (and the documentation even states that FUS only sends out one
event when it boots up).
'''
import time
import hashlib
import os

import psdb
from . import binaries
from .ws_client import WSClient


class FUSClient(object):
    def __init__(self, ipc):
        super(FUSClient, self).__init__()
        self.ipc     = ipc
        self.fw_name = 'FUS'
        assert self.ipc.mailbox.check_dit_key_fus()

    def _upgrade_firmware(self, data, fb):
        t, client = self.ipc.target, self

        assert client.get_ws_version() == 0
        assert hashlib.md5(data).hexdigest() == fb.md5sum
        assert len(data) % 4 == 0

        if len(data) % 8 == 4:
            data += b'\x00\x00\x00\x00'

        addr = fb.addr[t.flash.flash_size]
        t.flash.burn_dv([(addr, data)])

        print('Executing FUS_FW_UPGRADE...')
        try:
            r = t.ipc.system_channel.exec_fw_upgrade()
            print('FUS_FW_UPGRADE: %s' % r)
            assert r.status == 0x00
        except psdb.ProbeException:
            time.sleep(0.1)
            t, client = t.ipc._start_firmware(FUSClient)

        while True:
            try:
                r = t.ipc.system_channel.exec_get_state()
                print('FUS_GET_STATE: %s' % r)
                assert r.status != 0xFF
                if r.status == 0x00:
                    print('Finished in FUS mode.')
                    client.print_fus_version()
                    return t, client
                time.sleep(0.1)
            except psdb.ProbeException:
                time.sleep(0.1)
                t, client = t.ipc._start_firmware()
                if isinstance(client, WSClient):
                    print('Finished in WS firmware mode.')
                    return t, client

    def print_fus_version(self):
        version = self.get_fus_version()
        print('FUS version: 0x%08X (%u.%u.%u)' % (version,
                                                  ((version >> 24) & 0xFF),
                                                  ((version >> 16) & 0xFF),
                                                  ((version >>  8) & 0xFF)))
        version = self.get_ws_version()
        print(' WS version: 0x%08X (%u.%u.%u)' % (version,
                                                  ((version >> 24) & 0xFF),
                                                  ((version >> 16) & 0xFF),
                                                  ((version >>  8) & 0xFF)))

    def get_fus_version(self):
        '''
        Returns the FUS version field.
        '''
        return self.ipc.ap.read_32(self.ipc.mailbox.dit_addr + 12)

    def get_ws_version(self):
        '''
        Returns the WS firmware version field.
        '''
        return self.ipc.ap.read_32(self.ipc.mailbox.dit_addr + 20)

    def upgrade_fus_firmware(self, bin_dir):
        '''
        Upgrades to the next binary in the chain to the latest FUS firmware.
        The following images must be present in the bin_dir directory:

            stm32wb5x_FUS_fw_1_0_2.bin - 1.0.2 FUS binary
            stm32wb5x_FUS_fw.bin       - 1.1.0 FUS binary

        This process involves multiple reboots (3 or 4) which invalidates the
        debugger connection and target object.  The correct idiom for use is:

            target, client = client.upgrade_fus_firmware(bin_dir)
        '''
        t, client = self.ipc.target, self

        assert client.get_ws_version() == 0

        version = (client.get_fus_version() & 0xFFFFFF00)
        if version == binaries.FUS_BINARY_LATEST.version:
            print('FUS already at latest version %s.'
                  % binaries.FUS_BINARY_LATEST.version_str)
            return t, client
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
        Switches CPU2 into WS firmware mode.  This involves a reboot which
        invalidates the debugger connection and target object.  The correct
        idiom for use is:

            target, client = client.start_ws_firmware()
        '''
        assert self.get_ws_version() != 0

        while True:
            try:
                r = self.ipc.system_channel.exec_start_ws()
                print('FUS_START_WS: %s' % r)
                assert r.status != 0xFF
                time.sleep(0.1)
            except psdb.ProbeException:
                time.sleep(0.1)
                return self.ipc._start_firmware(WSClient)

    def delete_ws_firmware(self):
        '''
        Deletes the wireless firmware.  This may involve a reboot which
        invalidates the debugger connection and target object.  The correct
        idiom for use is:

            target, client = client.delete_ws_firmware()
        '''
        t, client = self.ipc.target, self

        assert client.get_ws_version() != 0

        try:
            r = t.ipc.system_channel.exec_fw_delete()
            print('FUS_FW_DELETE: %s' % r)
            assert r.status == 0x00
        except psdb.ProbeException:
            time.sleep(0.1)
            t, client = t.ipc._start_firmware(FUSClient)

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
                t, client = t.ipc._start_firmware(FUSClient)

        assert client.get_ws_version() == 0

        return t, client

    def upgrade_ws_firmware(self, bin_path):
        '''
        Upgrades the wireless firmware to the specified binary.  This involves
        multiple reboots which invalidate the debugger connection and target
        object.  The correct idiom for use is:

            target, client = client.upgrade_ws_firmware(bin_path)

        Typically, during the reboot cycle FUS automatically switches over to
        WS firmware mode, so the final client object will likely be a BLEClient
        instead of a FUSClient.
        '''
        assert self.get_ws_version() == 0

        with open(bin_path, 'rb') as f:
            data = f.read()
        md5sum = hashlib.md5(data).hexdigest()
        fb     = binaries.find_ws_binary(md5sum)

        return self._upgrade_firmware(data, fb)
