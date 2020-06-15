# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
from .ws_client import WSClient
from . import packet


class BLEClient(WSClient):
    def __init__(self, ipc, stack_type, fw_name):
        super(BLEClient, self).__init__(ipc, stack_type, fw_name)
        self.delegate = None

    def register_delegate(self, delegate):
        self.delegate = delegate

    def poll(self, timeout=None, dump=False):
        events = self.ipc.ble_channel.wait_and_pop_all_events(timeout=timeout,
                                                              dump=dump)
        for e in events:
            if isinstance(e, packet.BLECommandStatus):
                self.delegate.handle_command_status(e)
            elif isinstance(e, packet.BLECommandComplete):
                self.delegate.handle_command_complete(e)
            else:
                self.delegate.handle_event(e)
