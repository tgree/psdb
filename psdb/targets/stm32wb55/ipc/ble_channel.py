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
from . import gatt
from .. import ipcc

import struct
import uuid


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

# ACI HAL commands.
ACI_HAL_GET_FW_BUILD_NUMBER         = 0xFC00
ACI_HAL_WRITE_CONFIG_DATA           = 0xFC0C
ACI_HAL_READ_CONFIG_DATA            = 0xFC0D
ACI_HAL_SET_TX_POWER_LEVEL          = 0xFC0F
ACI_HAL_LE_TX_TEST_PACKET_NUMBER    = 0xFC14
ACI_HAL_TONE_START                  = 0xFC15
ACI_HAL_TONE_STOP                   = 0xFC16
ACI_HAL_GET_LINK_STATUS             = 0xFC17
ACI_HAL_SET_RADIO_ACTIVITY_MASK     = 0xFC18
ACI_HAL_GET_ANCHOR_PERIOD           = 0xFC19
ACI_HAL_SET_EVENT_MASK              = 0xFC1A
ACI_HAL_SET_SMP_ENG_CONFIG          = 0xFC1B
ACI_HAL_GET_PM_DEBUG_INFO           = 0xFC1C
ACI_HAL_READ_RADIO_REG              = 0xFC30
ACI_HAL_WRITE_RADIO_REG             = 0xFC31
ACI_HAL_READ_RAW_RSSI               = 0xFC32
ACI_HAL_RX_START                    = 0xFC33
ACI_HAL_RX_STOP                     = 0xFC34
ACI_HAL_STACK_RESET                 = 0xFC3B

# ACI GATT commands.
ACI_GATT_INIT                           = 0xFD01
ACI_GATT_ADD_SERVICE                    = 0xFD02
ACI_GATT_INCLUDE_SERVICE                = 0xFD03
ACI_GATT_ADD_CHAR                       = 0xFD04
ACI_GATT_ADD_CHAR_DESC                  = 0xFD05
ACI_GATT_UPDATE_CHAR_VALUE              = 0xFD06
ACI_GATT_DEL_CHAR                       = 0xFD07
ACI_GATT_DEL_SERVICE                    = 0xFD08
ACI_GATT_DEL_INCLUDE_SERVICE            = 0xFD09
ACI_GATT_SET_EVENT_MASK                 = 0xFD0A
ACI_GATT_EXCHANGE_CONFIG                = 0xFD0B
ACI_ATT_FIND_INFO_REQ                   = 0xFD0C
ACI_ATT_FIND_BY_TYPE_VALUE_REQ          = 0xFD0D
ACI_ATT_READ_BY_TYPE_REQ                = 0xFD0E
ACI_ATT_READ_BY_GROUP_TYPE_REQ          = 0xFD0F
ACI_ATT_PREPARE_WRITE_REQ               = 0xFD10
ACI_ATT_EXECUTE_WRITE_REQ               = 0xFD11
ACI_GATT_DISC_ALL_PRIMARY_SERVICES      = 0xFD12
ACI_GATT_DISC_PRIMARY_SERVICE_BY_UUID   = 0xFD13
ACI_GATT_FIND_INCLUDED_SERVICES         = 0xFD14
ACI_GATT_DISC_ALL_CHAR_OF_SERVICE       = 0xFD15
ACI_GATT_DISC_CHAR_BY_UUID              = 0xFD16
ACI_GATT_DISC_ALL_CHAR_DESC             = 0xFD17
ACI_GATT_READ_CHAR_VALUE                = 0xFD18
ACI_GATT_READ_USING_CHAR_UUID           = 0xFD19
ACI_GATT_READ_LONG_CHAR_VALUE           = 0xFD1A
ACI_GATT_READ_MULTIPLE_CHAR_VALUE       = 0xFD1B
ACI_GATT_WRITE_CHAR_VALUE               = 0xFD1C
ACI_GATT_WRITE_LONG_CHAR_VALUE          = 0xFD1D
ACI_GATT_WRITE_CHAR_RELIABLE            = 0xFD1E
ACI_GATT_WRITE_LONG_CHAR_DESC           = 0xFD1F
ACI_GATT_READ_LONG_CHAR_DESC            = 0xFD20
ACI_GATT_WRITE_CHAR_DESC                = 0xFD21
ACI_GATT_READ_CHAR_DESC                 = 0xFD22
ACI_GATT_WRITE_WITHOUT_RESP             = 0xFD23
ACI_GATT_SIGNED_WRITE_WITHOUT_RESP      = 0xFD24
ACI_GATT_CONFIRM_INDICATION             = 0xFD25
ACI_GATT_WRITE_RESP                     = 0xFD26
ACI_GATT_ALLOW_READ                     = 0xFD27
ACI_GATT_SET_SECURITY_PERMISSION        = 0xFD28
ACI_GATT_SET_DESC_VALUE                 = 0xFD29
ACI_GATT_READ_HANDLE_VALUE              = 0xFD2A
ACI_GATT_UPDATE_CHAR_VALUE_EXT          = 0xFD2C
ACI_GATT_DENY_READ                      = 0xFD2D
ACI_GATT_SET_ACCESS_PERMISSION          = 0xFD2E

# GAP commands.
ACI_GAP_SET_NON_DISCOVERABLE                       = 0xFC81
ACI_GAP_SET_LIMITED_DISCOVERABLE                   = 0xFC82
ACI_GAP_SET_DISCOVERABLE                           = 0xFC83
ACI_GAP_SET_DIRECT_CONNECTABLE                     = 0xFC84
ACI_GAP_SET_IO_CAPABILITY                          = 0xFC85
ACI_GAP_SET_AUTHENTICATION_REQUIREMENT             = 0xFC86
ACI_GAP_SET_AUTHORIZATION_REQUIREMENT              = 0xFC87
ACI_GAP_PASS_KEY_RESP                              = 0xFC88
ACI_GAP_AUTHORIZATION_RESP                         = 0xFC89
ACI_GAP_INIT                                       = 0xFC8A
ACI_GAP_SET_NON_CONNECTABLE                        = 0xFC8B
ACI_GAP_SET_UNDIRECTED_CONNECTABLE                 = 0xFC8C
ACI_GAP_SLAVE_SECURITY_REQ                         = 0xFC8D
ACI_GAP_UPDATE_ADV_DATA                            = 0xFC8E
ACI_GAP_DELETE_AD_TYPE                             = 0xFC8F
ACI_GAP_GET_SECURITY_LEVEL                         = 0xFC90
ACI_GAP_SET_EVENT_MASK                             = 0xFC91
ACI_GAP_CONFIGURE_WHITELIST                        = 0xFC92
ACI_GAP_TERMINATE                                  = 0xFC93
ACI_GAP_CLEAR_SECURITY_DB                          = 0xFC94
ACI_GAP_ALLOW_REBOND                               = 0xFC95
ACI_GAP_START_LIMITED_DISCOVERY_PROC               = 0xFC96
ACI_GAP_START_GENERAL_DISCOVERY_PROC               = 0xFC97
ACI_GAP_START_NAME_DISCOVERY_PROC                  = 0xFC98
ACI_GAP_START_AUTO_CONNECTION_ESTABLISH_PROC       = 0xFC99
ACI_GAP_START_GENERAL_CONNECTION_ESTABLISH_PROC    = 0xFC9A
ACI_GAP_START_SELECTIVE_CONNECTION_ESTABLISH_PROC  = 0xFC9B
ACI_GAP_CREATE_CONNECTION                          = 0xFC9C
ACI_GAP_TERMINATE_GAP_PROC                         = 0xFC9D
ACI_GAP_START_CONNECTION_UPDATE                    = 0xFC9E
ACI_GAP_SEND_PAIRING_REQ                           = 0xFC9F
ACI_GAP_RESOLVE_PRIVATE_ADDR                       = 0XFCA0
ACI_GAP_SET_BROADCAST_MODE                         = 0xFCA1
ACI_GAP_START_OBSERVATION_PROC                     = 0xFCA2
ACI_GAP_GET_BONDED_DEVICES                         = 0xFCA3
ACI_GAP_IS_DEVICE_BONDED                           = 0xFCA4
ACI_GAP_NUMERIC_COMPARISON_VALUE_CONFIRM_YESNO     = 0xFCA5
ACI_GAP_PASSKEY_INPUT                              = 0xFCA6
ACI_GAP_GET_OOB_DATA                               = 0xFCA7
ACI_GAP_SET_OOB_DATA                               = 0xFCA8
ACI_GAP_ADD_DEVICES_TO_RESOLVING_LIST              = 0xFCA9
ACI_GAP_REMOVE_BONDED_DEVICE                       = 0xFCAA

READ_CONFIG_DATA_OFFSETS = {
    0x00 : 6,
    0x06 : 2,
    0x08 : 16,
    0x18 : 16,
    0x80 : 6,
    }

WRITE_CONFIG_DATA_OFFSETS = {
    0x00 : 6,
    0x06 : 2,
    0x08 : 16,
    0x18 : 16,
    0x2E : 6,
    }


class BLEChannel(object):
    def __init__(self, ipc, cmd_channel, event_channel):
        super(BLEChannel, self).__init__()
        self.ipc           = ipc
        self.cmd_channel   = cmd_channel
        self.event_channel = event_channel
        self.services      = {}

    def _start_ble_command(self, opcode, payload=b''):
        self.ipc.mailbox.write_ble_command(opcode, payload)
        self.ipc.set_tx_flag(self.cmd_channel)

    def hci_reset(self):
        self._start_ble_command(HCI_RESET)
        return self.wait_and_pop_all_events()

    def hci_read_local_version_information(self):
        self._start_ble_command(HCI_READ_LOCAL_VERSION_INFORMATION)
        return self.wait_and_pop_all_events()

    def hci_read_bd_addr(self):
        self._start_ble_command(HCI_READ_BD_ADDR)
        return self.wait_and_pop_all_events()

    def hci_le_set_default_phy(self, all_phys, tx_phys, rx_phys):
        assert 0 <= all_phys and all_phys <= 3
        assert 0 <= tx_phys and tx_phys <= 3
        assert 0 <= rx_phys and rx_phys <= 3
        payload = struct.pack('<BBB', all_phys, tx_phys, rx_phys)
        self._start_ble_command(HCI_LE_SET_DEFAULT_PHY, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 1
        assert rsp[0].payload[0] == 0x00

    def aci_hal_read_config_data(self, offset):
        '''
        Reads a value from a low level configure data structure.  Depending on
        the offset, various data can be returned:

            Offset | Len | Description
            -------+-----+------------------------------------------------
            0x00   |  6  | Bluetooth public address
            0x06   |  2  | DIV used to derive CSRK
            0x08   | 16  | Encryption root key used to derive LTK and CSRK
            0x18   | 16  | Identity root key used to derive LTK and CSRK
            0x2E   |  6  | Static random address
            -------+-----+------------------------------------------------
        '''
        assert offset in READ_CONFIG_DATA_OFFSETS
        payload = struct.pack('<B', offset)
        self._start_ble_command(ACI_HAL_READ_CONFIG_DATA, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert rsp[0].payload[0]   == 0
        assert len(rsp[0].payload) == READ_CONFIG_DATA_OFFSETS[offset] + 2
        assert rsp[0].payload[1]   == READ_CONFIG_DATA_OFFSETS[offset]
        return rsp[0].payload[2:]

    def aci_hal_read_config_data_pubaddr(self):
        return self.aci_hal_read_config_data(0x00)

    def aci_hal_read_config_data_div(self):
        return self.aci_hal_read_config_data(0x06)

    def aci_hal_read_config_data_er(self):
        return self.aci_hal_read_config_data(0x08)

    def aci_hal_read_config_data_ir(self):
        return self.aci_hal_read_config_data(0x18)

    def aci_hal_read_config_data_random_address(self):
        return self.aci_hal_read_config_data(0x80)

    def aci_hal_write_config_data(self, offset, data):
        '''
        Writes a value to a low level configure data structure.  Depending on
        the offset, various data can be written.  Note that this is
        inconsistent with aci_hal_read_config_data() for the static random
        address field:

            Offset | Len | Description
            -------+-----+------------------------------------------------
            0x00   |  6  | Bluetooth public address
            0x06   |  2  | DIV used to derive CSRK
            0x08   | 16  | Encryption root key used to derive LTK and CSRK
            0x18   | 16  | Identity root key used to derive LTK and CSRK
            0x2E   |  6  | Static random address
            -------+-----+------------------------------------------------
        '''
        assert offset in WRITE_CONFIG_DATA_OFFSETS
        assert len(data) == WRITE_CONFIG_DATA_OFFSETS[offset]
        payload = struct.pack('<BB', offset, len(data)) + data
        self._start_ble_command(ACI_HAL_WRITE_CONFIG_DATA, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 1
        assert rsp[0].payload[0] == 0x00

    def aci_hal_write_config_data_pubaddr(self, ble_mac_addr):
        return self.aci_hal_write_config_data(0x00,
                                              bytes(reversed(ble_mac_addr)))

    def aci_hal_write_config_data_div(self, data):
        return self.aci_hal_write_config_data(0x06, data)

    def aci_hal_write_config_data_er(self, data):
        return self.aci_hal_write_config_data(0x08, data)

    def aci_hal_write_config_data_ir(self, data):
        return self.aci_hal_write_config_data(0x18, data)

    def aci_hal_write_config_data_random_address(self, data):
        return self.aci_hal_write_config_data(0x2E, data)

    def aci_hal_set_tx_power_level(self, enable_high_power, pa_level):
        assert isinstance(enable_high_power, bool)
        assert 0x00 <= pa_level and pa_level <= 0x1F
        payload = struct.pack('<BB', int(enable_high_power), pa_level)
        self._start_ble_command(ACI_HAL_SET_TX_POWER_LEVEL, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 1
        assert rsp[0].payload[0] == 0x00

    def aci_gatt_init(self):
        self._start_ble_command(ACI_GATT_INIT)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 1
        assert rsp[0].payload[0] == 0x00

    def aci_gatt_add_service(self, u, max_attribute_records, primary=True):
        if isinstance(u, uuid.UUID):
            payload = b'\x02' + bytes(reversed(u.bytes))
        elif isinstance(u, int):
            payload = b'\x01' + struct.pack('<H', u)
        else:
            raise Exception('Unsupported UUID type!')
        payload += b'\x01' if primary else b'\x02'
        payload += struct.pack('<B', max_attribute_records)
        self._start_ble_command(ACI_GATT_ADD_SERVICE, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 3
        assert rsp[0].payload[0] == 0x00
        service_handle = struct.unpack_from('<H', rsp[0].payload, 1)[0]
        service = gatt.Service(self, service_handle)
        self.services[service_handle] = service
        return service

    def aci_gatt_add_char(self, service_handle, u, char_max_len,
                          char_properties, security_permissions, gatt_evt_mask,
                          enc_key_size, is_variable):
        payload = struct.pack('<H', service_handle)
        if isinstance(u, uuid.UUID):
            payload += b'\x02' + bytes(reversed(u.bytes))
        elif isinstance(u, int):
            payload += b'\x01' + struct.pack('<H', u)
        else:
            raise Exception('Unsupported UUID type!')
        payload += struct.pack('<HBBBBB', char_max_len, char_properties,
                               security_permissions, gatt_evt_mask,
                               enc_key_size, is_variable)
        self._start_ble_command(ACI_GATT_ADD_CHAR, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 3
        assert rsp[0].payload[0] == 0x00
        char_handle = struct.unpack_from('<H', rsp[0].payload, 1)[0]
        return gatt.Characteristic(self.services[service_handle], char_handle)

    def aci_gatt_update_char_value(self, service_handle, char_handle,
                                   char_value, val_offset=0):
        payload = struct.pack('<HHBB', service_handle, char_handle, val_offset,
                              len(char_value)) + char_value
        self._start_ble_command(ACI_GATT_UPDATE_CHAR_VALUE, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 1
        assert rsp[0].payload[0] == 0x00

    def aci_gap_init(self, role, privacy_enabled, device_name):
        assert not (role & ~0xF)
        assert isinstance(privacy_enabled, bool)
        payload = struct.pack('<BBB', role, int(privacy_enabled),
                              len(device_name) + 2)
        self._start_ble_command(ACI_GAP_INIT, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 7
        assert rsp[0].payload[0] == 0x00
        (gap_service_handle,
         dev_name_char_handle,
         appearance_char_handle) = struct.unpack('<xHHH', rsp[0].payload)
        gap_service     = gatt.Service(self, gap_service_handle)
        dev_name_char   = gatt.Characteristic(gap_service, dev_name_char_handle)
        appearance_char = gatt.Characteristic(gap_service,
                                              appearance_char_handle)

        self.services[gap_service_handle] = gap_service
        return gap_service, dev_name_char, appearance_char

    def aci_gap_set_io_capability(self, io_capability):
        assert 0 <= io_capability and io_capability <= 4
        payload = struct.pack('<B', io_capability)
        self._start_ble_command(ACI_GAP_SET_IO_CAPABILITY, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 1
        assert rsp[0].payload[0] == 0x00

    def aci_gap_set_authentication_requirement(self, bonding_mode, mitm_mode,
                                               sc_support,
                                               keypress_notification_support,
                                               min_encryption_key_size,
                                               max_encryption_key_size,
                                               use_fixed_pin, fixed_pin,
                                               identity_address_type):
        assert bonding_mode in (0, 1)
        assert mitm_mode in (0, 1)
        assert sc_support in (0, 1, 2)
        assert keypress_notification_support in (0, 1)
        assert use_fixed_pin in (0, 1)
        assert 0 <= fixed_pin and fixed_pin <= 999999
        assert identity_address_type in (0, 1)
        payload = struct.pack('<BBBBBBBLB', bonding_mode, mitm_mode, sc_support,
                              keypress_notification_support,
                              min_encryption_key_size, max_encryption_key_size,
                              use_fixed_pin, fixed_pin, identity_address_type)
        self._start_ble_command(ACI_GAP_SET_AUTHENTICATION_REQUIREMENT, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 1
        assert rsp[0].payload[0] == 0x00

    def aci_gap_set_discoverable(self, advertising_type,
                                 advertising_interval_min,
                                 advertising_interval_max,
                                 own_address_type,
                                 advertising_filter_policy,
                                 local_name,
                                 service_uuid_list,
                                 slave_conn_interval_min,
                                 slave_conn_interval_max):
        payload  = struct.pack('<BHHBBB', advertising_type,
                               advertising_interval_min,
                               advertising_interval_max, own_address_type,
                               advertising_filter_policy, len(local_name))
        payload += local_name
        uuid_bytes = b''
        for u in service_uuid_list:
            if isinstance(u, uuid.UUID):
                uuid_bytes += b'\x06'
                uuid_bytes += bytes(reversed(u.bytes))
            elif isinstance(u, int):
                uuid_bytes += b'\x02'
                uuid_bytes += struct.pack('<H', u)
            else:
                raise Exception('Unsupported UUID type!')
        payload += struct.pack('<B', len(uuid_bytes))
        payload += uuid_bytes
        payload += struct.pack('<HH', slave_conn_interval_min,
                               slave_conn_interval_max)
        self._start_ble_command(ACI_GAP_SET_DISCOVERABLE, payload)
        rsp = self.wait_and_pop_all_events()
        assert len(rsp) == 1
        assert len(rsp[0].payload) == 1
        assert rsp[0].payload[0] == 0x00

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
                self.ipc.mm_channel.release_posted_events()
                return events

            print(event)
            events.append(event)

            if not isinstance(event, (packet.BLECommandStatus,
                                      packet.BLECommandComplete)):
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
