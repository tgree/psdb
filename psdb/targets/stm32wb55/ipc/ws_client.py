# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.


class WSClient(object):
    def __init__(self, ipc):
        super(WSClient, self).__init__()
        self.ipc = ipc
        assert not self.ipc.mailbox.check_dit_key_fus()
