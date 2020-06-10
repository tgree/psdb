# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.


class Service(object):
    def __init__(self, ble_channel, service_handle):
        self.ble_channel    = ble_channel
        self.service_handle = service_handle

    def update_char_value(self, char_handle, char_value, val_offset=0):
        self.ble_channel.aci_gatt_update_char_value(self.service_handle,
                                                    char_handle, char_value,
                                                    val_offset)


class Characteristic(object):
    def __init__(self, service, char_handle):
        self.service     = service
        self.char_handle = char_handle

    def update_value(self, char_value, val_offset=0):
        self.service.update_char_value(self.char_handle, char_value, val_offset)
