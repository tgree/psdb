# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import psdb.probes
import time


FUS_GET_STATE               = 0xFC52
FUS_FW_UPGRADE              = 0xFC54
FUS_FW_DELETE               = 0xFC55
FUS_UPDATE_AUTH_KEY         = 0xFC56
FUS_LOCK_AUTH_KEY           = 0xFC57
FUS_STORE_USR_KEY           = 0xFC58
FUS_LOAD_USR_KEY            = 0xFC59
FUS_START_WS                = 0xFC5A
FUS_LOCK_USR_KEY            = 0xFC5D
FUS_UNLOAD_USR_KEY          = 0xFC5E
FUS_ACTIVATE_ANTIROLLBACK   = 0xFC5F


class SystemChannel(object):
    def __init__(self, ipc, cmd_rsp_channel, event_channel):
        super(SystemChannel, self).__init__()
        self.ipc             = ipc
        self.cmd_rsp_channel = cmd_rsp_channel
        self.event_channel   = event_channel

    def _start_sys_command(self, opcode, payload=b''):
        self.ipc.mailbox.write_sys_command(opcode, payload)
        self.ipc.set_tx_flag(self.cmd_rsp_channel)

    def _wait_sys_response(self):
        self.ipc.wait_tx_free(self.cmd_rsp_channel)
        return self.ipc.mailbox.read_sys_response()

    def exec_sys_command(self, opcode, payload=b''):
        self._start_sys_command(opcode, payload)
        return self._wait_sys_response()

    def exec_get_state(self):
        return self.exec_sys_command(FUS_GET_STATE)

    def exec_fw_delete(self):
        return self.exec_sys_command(FUS_FW_DELETE)

    def exec_fw_upgrade(self):
        return self.exec_sys_command(FUS_FW_UPGRADE)

    def exec_start_ws(self):
        return self.exec_sys_command(FUS_START_WS)

    def pop_all_events(self):
        '''
        Pop and return all events from the system event queue.
        '''
        if not self.ipc.get_rx_flag(self.event_channel):
            return []

        events = []
        while True:
            event = self.ipc.mailbox.pop_sys_event()
            if event is None:
                self.ipc.clear_rx_flag(self.event_channel)
                return events

            print(event)
            events.append(event)
            self.ipc.mailbox.push_mm_free_event(event)

    def wait_and_pop_all_events(self, timeout=None):
        '''
        Waits for the event flag to be set and then pops all events.
        '''
        events = []
        while not events:
            self.ipc.wait_rx_occupied(self.event_channel, timeout=timeout)
            new_events = self.pop_all_events()
            if not new_events:
                print('Empty event list?')

            events += new_events

        return events
