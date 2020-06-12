# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
'''
System commands are issued on the system command/response channel (IPCC
channel 2) using half-duplex channel mode.  You write the command into
sys_table->pcmd_buffer and then set the channel TX flag.  The coprocessor
will take the interrupt and execute the command.  When the coprocessor has
done executing the command, it will write the response packet back into the
same sys_table->pcmd_buffer and then clear the TX flag (the RX flag from its
perspective), at which point we'll get a TX free interrupt.  That interrupt
tells us both that the response is ready and that we can overwrite it at our
convenience to send a new command.

Asynchronous events from the firmware are issued on the system event channel
(also IPCC channel 2).  When an event becomes available, it will be queued on
to the sys_table->sys_queue and then we will receive a channel RX occupied
interrupt.  FUS is buggy and does not set the queue sentinel's prev (tail)
pointer properly.  The head pointer is always the MM Spare System Event Buffer.
The only safe way to process the queue is to repeatedly pop_front() under a
while(!sys_table->sys_queue.empty()) loop.  The BLE firmware does not have this
bug and its queue pointers are in the MM BLE Pool area instead.
'''
from .. import ipcc

import struct


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

BLE_INIT                    = 0xFC66

# Ready event indicating the firmware is ready to accept commands.
SHCI_SUBEVTCODE_READY   = 0x9200
EVT_PAYLOAD_WS_RUNNING  = b'\x00'
EVT_PAYLOAD_FUS_RUNNING = b'\x01'


def is_fus_ready_event(event):
    return (event.subevtcode == SHCI_SUBEVTCODE_READY and
            event.payload == EVT_PAYLOAD_FUS_RUNNING)


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

    def exec_ble_init(self, num_gatt_attributes=68, num_gatt_services=8,
                      att_value_array_size=1344, num_link=8,
                      data_length_extension=True,
                      prepare_write_list_size=0x3A, mblock_count=0x79,
                      max_att_mtu=156, slave_sca=500,
                      master_sca=0, lse_source=0,
                      max_conn_event_length=0xFFFFFFFF,
                      hse_startup_time=0x148, viterbi_mode=1, ll_only=0,
                      hw_version=0):
        payload = struct.pack('<LLHHHBBBBHHBBLHBBB',
                              0, 0,
                              num_gatt_attributes,
                              num_gatt_services,
                              att_value_array_size,
                              num_link,
                              int(data_length_extension),
                              prepare_write_list_size,
                              mblock_count,
                              max_att_mtu,
                              slave_sca,
                              master_sca,
                              lse_source,
                              max_conn_event_length,
                              hse_startup_time,
                              viterbi_mode,
                              ll_only,
                              hw_version)
        assert len(payload) == 33
        return self.exec_sys_command(BLE_INIT, payload=payload)

    def pop_all_events(self, dump=False):
        '''
        Pop and return all events from the system event queue.
        '''
        if not self.ipc.get_rx_flag(self.event_channel):
            return []

        if dump:
            self.ipc.mailbox.sys_queue.dump()

        events = []
        while True:
            event = self.ipc.mailbox.pop_sys_event()
            if event is None:
                self.ipc.clear_rx_flag(self.event_channel)
                self.ipc.mm_channel.release_posted_events()
                return events

            print(event)
            events.append(event)

            # The only FUS event is the initial Ready event and since FUS
            # doesn't implement the MM channel, it shouldn't be returned.
            if is_fus_ready_event(event):
                continue

            self.ipc.mm_channel.post_event(event)

    def wait_and_pop_all_events(self, timeout=None, dump=False):
        '''
        Waits for the event flag to be set and then pops all events.  Returns
        an empty list if the timeout expired.
        '''
        try:
            self.ipc.wait_rx_occupied(self.event_channel, timeout=timeout)
            return self.pop_all_events(dump=dump)
        except ipcc.TimeoutError:
            return []
