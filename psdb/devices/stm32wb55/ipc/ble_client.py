# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
from .ws_client import WSClient


class BLEClient(WSClient):
    def __init__(self, ipc, stack_type, fw_name):
        super(BLEClient, self).__init__(ipc, stack_type, fw_name)
