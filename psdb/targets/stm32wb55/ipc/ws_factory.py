# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
from .ws_client import WSClient
from .ble_client import BLEClient


class WS_TYPE(object):
    UNKNOWN               = -1
    BLE_STANDARD          = 0x01
    BLE_HCI               = 0x02
    BLE_LIGHT             = 0x03
    THREAD_FTD            = 0x10
    THREAD_MTD            = 0x11
    ZIGBEE_FFD            = 0x30
    ZIGBEE_RFD            = 0x31
    MAC                   = 0x40
    BLE_THREAD_FTD_STATIC = 0x50
    MAC_802154_LLD_TESTS  = 0x60
    MAC_802154_PHY_VALID  = 0x61
    BLE_PHY_VALID         = 0x62
    BLE_LLD_TESTS         = 0x63
    BLE_RLV               = 0x64
    MAC_802154_RLV        = 0x65
    BLE_ZIGBEE_FFD_STATIC = 0x70


WS_NAME = {
    WS_TYPE.UNKNOWN               : 'Unknown',
    WS_TYPE.BLE_STANDARD          : 'BLE Standard',
    WS_TYPE.BLE_HCI               : 'BLE HCI',
    WS_TYPE.BLE_LIGHT             : 'BLE Light',
    WS_TYPE.THREAD_FTD            : 'Thread FTD',
    WS_TYPE.THREAD_MTD            : 'Thread MTD',
    WS_TYPE.ZIGBEE_FFD            : 'Zigbee FFD',
    WS_TYPE.ZIGBEE_RFD            : 'Zigbee RFD',
    WS_TYPE.MAC                   : 'MAC',
    WS_TYPE.BLE_THREAD_FTD_STATIC : 'BLE Thread FTD Static',
    WS_TYPE.MAC_802154_LLD_TESTS  : '802154 LLD Tests',
    WS_TYPE.MAC_802154_PHY_VALID  : '802154 PHY Valid',
    WS_TYPE.BLE_PHY_VALID         : 'BLE PHY Valid',
    WS_TYPE.BLE_LLD_TESTS         : 'BLE LLD Tests',
    WS_TYPE.BLE_RLV               : 'BLE RLV',
    WS_TYPE.MAC_802154_RLV        : '802154 RLV',
    WS_TYPE.BLE_ZIGBEE_FFD_STATIC : 'BLE Zigbee FFD Static',
    }


def make_client(ipc, stack_type):
    fw_name = WS_NAME.get(stack_type, 'Unknown')
    if stack_type == WS_TYPE.BLE_STANDARD:
        return BLEClient(ipc, stack_type, fw_name)
    return WSClient(ipc, stack_type, fw_name)
