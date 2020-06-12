# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import time

import psdb


class WSClient(object):
    def __init__(self, ipc, stack_type, fw_name):
        super(WSClient, self).__init__()
        self.ipc        = ipc
        self.stack_type = stack_type
        self.fw_name    = fw_name
        assert not self.ipc.mailbox.check_dit_key_fus()

    def start_fus_firmware(self):
        '''
        Switches CPU2 into FUS mode.  This involves a reboot which invalidates
        the debugger connection and target object.  The correct idiom for use
        is:

            target, client = client.start_fus_firmware()
        '''
        while True:
            try:
                r = self.ipc.system_channel.exec_get_state()
                print('FUS_GET_STATE: %s' % r)
                time.sleep(0.1)
            except psdb.ProbeException:
                from .fus_client import FUSClient
                time.sleep(0.1)
                return self.ipc._start_firmware(FUSClient)

    def print_ws_version(self):
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
        info = self.get_ws_info()
        print('    WS info: 0x%08X' % info)
        print('    FW name: %s' % self.fw_name)

    def get_fus_version(self):
        '''
        Returns the FUS version field.
        '''
        return self.ipc.ap.read_32(self.ipc.mailbox.dit_addr + 4)

    def get_ws_version(self):
        '''
        Returns the WS firmware version field.
        '''
        return self.ipc.ap.read_32(self.ipc.mailbox.dit_addr + 16)

    def get_ws_info(self):
        '''
        Returns the WS firmware info stack field.
        '''
        return self.ipc.ap.read_32(self.ipc.mailbox.dit_addr + 24)
