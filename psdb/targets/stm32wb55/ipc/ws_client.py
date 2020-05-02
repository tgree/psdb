# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import time

import psdb


class WSClient(object):
    def __init__(self, ipc):
        super(WSClient, self).__init__()
        self.ipc = ipc
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
