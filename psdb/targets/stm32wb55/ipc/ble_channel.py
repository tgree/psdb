# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
'''
BLE commands are issued on the BLE command channel (IPCC channel 1).  Commands
are issued by writing the command to the BLE Table's BLE Command Buffer and
then setting the channel flag.

BLE events are received on the BLE event channel (IPCC channel 1).  Commands
can generate up to two completion events: an optional "status" event that acts
as an acknowledgement that the chip has started to command and then a
"completion" event indicating the actual command completion status.

The status and completion events get populated into two static mailbox buffers
and don't need to be returned to the firmware via the MM channel, but the
client does need to be done with the event buffers before submitting a new
command since the new command overwrites the completion buffer (not to mention
the obvious race condition).
'''
from . import packet


# HCI Commands
HCI_DISCONNECT                                = 0x0406
HCI_READ_REMOTE_VERSION_INFORMATION           = 0x041D
HCI_SET_EVENT_MASK                            = 0x0C01
HCI_RESET                                     = 0x0C03
HCI_READ_TRANSMIT_POWER_LEVEL                 = 0x0C2D
HCI_SET_CONTROLLER_TO_HOST_FLOW_CONTROL       = 0x0C31
HCI_HOST_BUFFER_SIZE                          = 0x0C33
HCI_HOST_NUMBER_OF_COMPLETED_PACKETS          = 0x0C35
HCI_READ_LOCAL_VERSION_INFORMATION            = 0x1001
HCI_READ_LOCAL_SUPPORTED_COMMANDS             = 0x1002
HCI_READ_LOCAL_SUPPORTED_FEATURES             = 0x1003
HCI_READ_BD_ADDR                              = 0x1009
HCI_READ_RSSI                                 = 0x1405
HCI_LE_SET_EVENT_MASK                         = 0x2001
HCI_LE_READ_BUFFER_SIZE                       = 0x2002
HCI_LE_READ_LOCAL_SUPPORTED_FEATURES          = 0x2003
HCI_LE_SET_RANDOM_ADDRESS                     = 0x2005
HCI_LE_SET_ADVERTISING_PARAMETERS             = 0x2006
HCI_LE_READ_ADVERTISING_CHANNEL_TX_POWER      = 0x2007
HCI_LE_SET_ADVERTISING_DATA                   = 0x2008
HCI_LE_SET_SCAN_ENABLE                        = 0x2009
HCI_LE_SET_ADVERTISE_ENABLE                   = 0x200A
HCI_LE_SET_SCAN_PARAMETERS                    = 0x200B
HCI_LE_SET_SCAN_ENABLE                        = 0x200C
HCI_LE_CREATE_CONNECTION                      = 0x200D
HCI_LE_CREATE_CONNECTION_CANCEL               = 0x200E
HCI_LE_READ_WHITE_LIST_SIZE                   = 0x200F
HCI_LE_CLEAR_WHITE_LIST                       = 0x2010
HCI_LE_ADD_DEVICE_TO_WHITE_LIST               = 0x2011
HCI_LE_REMOVE_DEVICE_FROM_WHITE_LIST          = 0x2012
HCI_LE_CONNECTION_UPDATE                      = 0x2013
HCI_LE_SET_HOST_CHANNEL_CLASSIFICATION        = 0x2014
HCI_LE_READ_CHANNEL_MAP                       = 0x2015
HCI_LE_READ_REMOTE_USED_FEATURES              = 0x2016
HCI_LE_ENCRYPT                                = 0x2017
HCI_LE_RAND                                   = 0x2018
HCI_LE_START_ENCRYPTION                       = 0x2019
HCI_LE_LONG_TERM_KEY_REQUEST_REPLY            = 0x201A
HCI_LE_LONG_TERM_KEY_REQUESTED_NEGATIVE_REPLY = 0x201B
HCI_LE_READ_SUPPORTED_STATES                  = 0x201C
HCI_LE_SET_DATA_LENGTH                        = 0x2022
HCI_LE_READ_SUGGESTED_DEFAULT_DATA_LENGTH     = 0x2023
HCI_LE_WRITE_SUGGESTED_DEFAULT_DATA_LENGTH    = 0x2024
HCI_LE_READ_LOCAL_P256_PUBLIC_KEY             = 0x2025
HCI_LE_GENERATE_DHKEY                         = 0x2026
HCI_LE_ADD_DEVICE_TO_RESOLVING_LIST           = 0x2027
HCI_LE_REMOVE_DEVICE_FROM_RESOLVING_LIST      = 0x2028
HCI_LE_CLEAR_RESOLVING_LIST                   = 0x2029
HCI_LE_READ_RESOLVING_LIST_SIZE               = 0x202A
HCI_LE_READ_PEER_RESOLVABLE_ADDRESS           = 0x202B
HCI_LE_READ_LOCAL_RESOLVABLE_ADDRESS          = 0x202C
HCI_LE_SET_ADDRESS_RESOLUTION_ENABLE          = 0x202D
HCI_LE_SET_RESOLVABLE_PRIVATE_ADDRESS_TIMEOUT = 0x202E
HCI_LE_READ_MAXIMUM_DATA_LENGTH               = 0x202F
HCI_LE_READ_PHY                               = 0x2030
HCI_LE_SET_DEFAULT_PHY                        = 0x2031
HCI_LE_SET_PHY                                = 0x2032


class BLEChannel(object):
    def __init__(self, ipc, cmd_channel, event_channel):
        super(BLEChannel, self).__init__()
        self.ipc           = ipc
        self.cmd_channel   = cmd_channel
        self.event_channel = event_channel

    def _start_ble_command(self, opcode, payload=b''):
        self.ipc.mailbox.write_ble_command(opcode, payload)
        self.ipc.set_tx_flag(self.cmd_channel)

    def hci_read_local_version_information(self):
        self._start_ble_command(HCI_READ_LOCAL_VERSION_INFORMATION)
        return self.wait_and_pop_all_events()

    def hci_read_bd_addr(self):
        self._start_ble_command(HCI_READ_BD_ADDR)
        return self.wait_and_pop_all_events()

    def pop_all_events(self, dump=False):
        '''
        Pop and return all events from the BLE event queue.
        '''
        if not self.ipc.get_rx_flag(self.event_channel):
            return []

        if dump:
            self.ipc.mailbox.ble_evt_queue.dump()

        events = []
        while True:
            event = self.ipc.mailbox.pop_ble_event()
            if event is None:
                self.ipc.clear_rx_flag(self.event_channel)
                return events

            print(event)
            events.append(event)

            if not isinstance(event, (packet.BLECommandStatus,
                                      packet.BLECommandComplete)):
                self.ipc.mailbox.push_mm_free_event(event)

    def wait_and_pop_all_events(self, timeout=None, dump=False):
        '''
        Waits for the event flag to be set and then pops all events.
        '''
        events = []
        while not events:
            self.ipc.wait_rx_occupied(self.event_channel, timeout=timeout)
            new_events = self.pop_all_events(dump=dump)
            if not new_events:
                return events

            events += new_events

        return events
