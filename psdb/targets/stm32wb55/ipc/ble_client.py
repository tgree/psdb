# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
from .ws_client import WSClient


class BLEClient(WSClient):
    def __init__(self, ipc):
        super(BLEClient, self).__init__(ipc)
