# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.


class FUSClient(object):
    def __init__(self, ipc):
        super(FUSClient, self).__init__()
        self.ipc = ipc
        assert self.ipc.mailbox.check_dit_key_fus()
