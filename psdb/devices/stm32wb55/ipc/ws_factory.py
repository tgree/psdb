# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
from .ws_client import WSClient
from .ble_client import BLEClient


class WS_TYPE(object):
    '''
    These are all defined in the STM32CubeWB git repository under:

        Middlewares/ST/STM32_WPAN/interface/patterns/ble_thread/shci/shci.h
    '''
    UNKNOWN                   = -1
    BLE_FULL                  = 0x01
    BLE_HCI                   = 0x02
    BLE_LIGHT                 = 0x03
    BLE_BEACON                = 0x04
    BLE_BASIC                 = 0x05
    BLE_FULL_EXT_ADV          = 0x06
    BLE_HCI_EXT_ADV           = 0x07
    THREAD_FTD                = 0x10
    THREAD_MTD                = 0x11
    ZIGBEE_FFD                = 0x30
    ZIGBEE_RFD                = 0x31
    MAC                       = 0x40
    BLE_THREAD_FTD_STATIC     = 0x50
    BLE_THREAD_FTD_DYAMIC     = 0x51
    MAC_802154_LLD_TESTS      = 0x60
    MAC_802154_PHY_VALID      = 0x61
    BLE_PHY_VALID             = 0x62
    BLE_LLD_TESTS             = 0x63
    BLE_RLV                   = 0x64
    MAC_802154_RLV            = 0x65
    BLE_ZIGBEE_FFD_STATIC     = 0x70
    BLE_ZIGBEE_RFD_STATIC     = 0x71
    BLE_ZIGBEE_FFD_DYNAMIC    = 0x78
    BLE_ZIGBEE_RFD_DYNAMIC    = 0x79
    RLV                       = 0x80
    BLE_MAC_STATIC            = 0x90


WS_NAME = {
    WS_TYPE.BLE_FULL               : 'BLE Full',
    WS_TYPE.BLE_HCI                : 'BLE HCI',
    WS_TYPE.BLE_LIGHT              : 'BLE Light',
    WS_TYPE.BLE_BEACON             : 'BLE Beacon',
    WS_TYPE.BLE_BASIC              : 'BLE Basic',
    WS_TYPE.BLE_FULL_EXT_ADV       : 'BLE Full Ext Adv',
    WS_TYPE.BLE_HCI_EXT_ADV        : 'BLE HCI Ext Adv',
    WS_TYPE.THREAD_FTD             : 'Thread FTD',
    WS_TYPE.THREAD_MTD             : 'Thread MTD',
    WS_TYPE.ZIGBEE_FFD             : 'Zigbee FFD',
    WS_TYPE.ZIGBEE_RFD             : 'Zigbee RFD',
    WS_TYPE.MAC                    : 'MAC',
    WS_TYPE.BLE_THREAD_FTD_STATIC  : 'BLE Thread FTD Static',
    WS_TYPE.BLE_THREAD_FTD_DYAMIC  : 'BLE Thread FTD Dynamic',
    WS_TYPE.MAC_802154_LLD_TESTS   : '802154 LLD Tests',
    WS_TYPE.MAC_802154_PHY_VALID   : '802154 PHY Valid',
    WS_TYPE.BLE_PHY_VALID          : 'BLE PHY Valid',
    WS_TYPE.BLE_LLD_TESTS          : 'BLE LLD Tests',
    WS_TYPE.BLE_RLV                : 'BLE RLV',
    WS_TYPE.MAC_802154_RLV         : '802154 RLV',
    WS_TYPE.BLE_ZIGBEE_FFD_STATIC  : 'BLE Zigbee FFD Static',
    WS_TYPE.BLE_ZIGBEE_RFD_STATIC  : 'BLE Zigbee RFD Static',
    WS_TYPE.BLE_ZIGBEE_FFD_DYNAMIC : 'BLE Zigbee FFD Dynamic',
    WS_TYPE.BLE_ZIGBEE_RFD_DYNAMIC : 'BLE Zigbee RFD Dynamic',
    WS_TYPE.RLV                    : 'RLV',
    WS_TYPE.BLE_MAC_STATIC         : 'BLE MAC Static',
    }


def make_client(ipc, stack_type):
    fw_name = WS_NAME.get(stack_type, 'Unknown (0x%02X)' % stack_type)
    if stack_type == WS_TYPE.BLE_FULL:
        return BLEClient(ipc, stack_type, fw_name)
    return WSClient(ipc, stack_type, fw_name)
