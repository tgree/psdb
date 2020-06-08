# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
'''
Firmware events (on either the Sytem or BLE channels) are allocated by the
wireless firmware from its memory pool and then posted to us for consumption.
When we are done with the event, we must use the Memory Manager mailbox queue
and channel to post the buffers back to the wireless firmware for reuse.

Buffer release is performed via the MM release channel (IPCC channel 4) by
queueing the buffer(s) on the p_mem_manager_table->pevt_free_buffer_queue and
then setting the channel TX flag.  The coprocessor will pop the buffers for
reuse and clear the TX flag when the queue can be used to release more buffers.
'''


class MMChannel(object):
    def __init__(self, ipc, cmd_channel):
        super(MMChannel, self).__init__()
        self.ipc           = ipc
        self.cmd_channel   = cmd_channel
        self.posted_events = []

    def post_event(self, evt):
        '''
        Pushes an event to the memory manager return event queue tail.  This
        queue is used to return events back to the firmware that it allocated
        out of its memory pool when posting an event.
        '''
        assert self.ipc.is_tx_free(self.cmd_channel)
        self.ipc.mailbox.return_evt_queue.push(evt.addr)
        self.posted_events.append(evt)

    def release_posted_events(self):
        '''
        Sets the IPCC event flag, triggering the wireless firmware to consume
        the posted events.  Blocks until the events have been freed.
        '''
        if not self.posted_events:
            return

        print('Releasing events: %s' % self.posted_events)
        self.ipc.set_tx_flag(self.cmd_channel)
        self.ipc.wait_tx_free(self.cmd_channel)
        assert self.ipc.mailbox.return_evt_queue.is_empty()
        self.posted_events = []
