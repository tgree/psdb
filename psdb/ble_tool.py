#!/usr/bin/env python3
# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import psdb.probes
import psdb.targets
from psdb.util import hexify
from psdb.devices.stm32wb55.ipc import gatt

import argparse
import threading
import struct
import time
import uuid
import sys


RUNNING = True

CFG_IR = b'\x12\x34\x56\x78\x9A\xBC\xDE\xF0\x12\x34\x56\x78\x9A\xBC\xDE\xF0'
CFG_ER = b'\xFE\xDC\xBA\x09\x87\x65\x43\x21\xFE\xDC\xBA\x09\x87\x65\x43\x21'

DEV_NAME       = b'PSDBTest'
DEV_APPEARANCE = struct.pack('<H', 832)
LOCAL_NAME     = b'\x09' + DEV_NAME
PSDB_UUID      = uuid.UUID('f4182738-aaed-11ea-9ce0-784f435eb986')
PSDB_CHAR      = uuid.UUID('210c8390-aaf5-11ea-9ce0-784f435eb986')

TICK_PERIOD_SEC = 1


class BLEDelegate(object):
    IDLE                    = 0
    WAIT_HCI_RESET              = 1
    WAIT_READ_PUBADDR           = 2
    WAIT_READ_IR                = 3
    WAIT_READ_ER                = 4
    WAIT_READ_RANDOM_ADDR       = 5
    WAIT_WRITE_PUBADDR          = 6
    WAIT_WRITE_IRKEY            = 7
    WAIT_WRITE_ERKEY            = 8
    WAIT_WRITE_RANDOM_ADDR      = 9
    WAIT_SET_TX_POWER_LEVEL     = 10
    WAIT_GATT_INIT              = 11
    WAIT_GAP_INIT               = 12
    WAIT_SET_DEVICE_NAME        = 13
    WAIT_SET_DEVICE_APPEARANCE  = 14
    WAIT_ADD_PSDB_SERVICE       = 15
    WAIT_ADD_PSDB_CHAR          = 16
    WAIT_UPDATE_PSDB_CHAR       = 17
    WAIT_SET_DEFAULT_PHY        = 18
    WAIT_SET_IO_CAPABILITY      = 19
    WAIT_SET_AUTH_REQUIREMENT   = 20
    WAIT_SET_DISCOVERABLE       = 21

    WAIT_INCREMENT_PSDB_CHAR    = 100

    WAIT_EVENTS                 = 1000

    def __init__(self, client):
        self.client      = client
        self.target      = client.ipc.target
        self.ble_channel = self.client.ipc.ble_channel
        self.state       = self.IDLE
        self.psdb_value  = 0x12

    def start(self):
        self.client.register_delegate(self)

        print('Starting BLE firmware...')
        print(self.client.ipc.system_channel.exec_ble_init())

        print('Resetting HCI...')
        self.ble_channel.hci_reset()
        self.state = self.WAIT_HCI_RESET

    def handle_event(self, event):
        print('Random event: %s' % event)

    def handle_command_status(self, event):
        print('Random command status: %s' % event)
        raise Exception('Unexpected COMMAND_STATUS event! %s' % event)

    def handle_command_complete(self, event):
        print('Command complete: %s' % event)
        if self.state == self.WAIT_HCI_RESET:
            assert event.payload == b'\x00'
            print('Reading CONFIG_DATA_PUBADDR...')
            self.ble_channel.aci_hal_read_config_data_pubaddr()
            self.state = self.WAIT_READ_PUBADDR

        elif self.state == self.WAIT_READ_PUBADDR:
            assert event.payload[0]   == 0
            assert len(event.payload) == 8
            assert event.payload[1]   == 6
            print('PUBADDR: %s' % hexify(event.payload[2:]))
            print('Reading IR key...')
            self.ble_channel.aci_hal_read_config_data_ir()
            self.state = self.WAIT_READ_IR

        elif self.state == self.WAIT_READ_IR:
            assert event.payload[0]   == 0
            assert len(event.payload) == 18
            assert event.payload[1]   == 16
            print('IRK: %s' % hexify(event.payload[2:]))
            print('Reading ER key...')
            self.ble_channel.aci_hal_read_config_data_er()
            self.state = self.WAIT_READ_ER

        elif self.state == self.WAIT_READ_ER:
            assert event.payload[0]   == 0
            assert len(event.payload) == 18
            assert event.payload[1]   == 16
            print('ERK: %s' % hexify(event.payload[2:]))
            print('Reading static random address...')
            self.ble_channel.aci_hal_read_config_data_random_address()
            self.state = self.WAIT_READ_RANDOM_ADDR

        elif self.state == self.WAIT_READ_RANDOM_ADDR:
            assert event.payload[0]   == 0
            assert len(event.payload) == 8
            assert event.payload[1]   == 6
            print('RA: %s' % hexify(event.payload[2:]))
            print('Writing UDN-generated public address...')
            self.ble_channel.aci_hal_write_config_data_pubaddr(
                    self.target.ble_mac_addr)
            self.state = self.WAIT_WRITE_PUBADDR

        elif self.state == self.WAIT_WRITE_PUBADDR:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Writing IR key...')
            self.ble_channel.aci_hal_write_config_data_ir(CFG_IR)
            self.state = self.WAIT_WRITE_IRKEY

        elif self.state == self.WAIT_WRITE_IRKEY:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Writing ER key...')
            self.ble_channel.aci_hal_write_config_data_er(CFG_ER)
            self.state = self.WAIT_WRITE_ERKEY

        elif self.state == self.WAIT_WRITE_ERKEY:
            # Write a static random address.  The comments in the ST code
            # indicate that the "two upper bits shall be set to 1" but unless
            # there is some amazing byte-swapping going on here, this code
            # doesn't do that.
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Writing static random address...')
            rand_addr = struct.pack('<LH', self.target.uid64_udn, 0xED6E)
            self.ble_channel.aci_hal_write_config_data_random_address(rand_addr)
            self.state = self.WAIT_WRITE_RANDOM_ADDR

        elif self.state == self.WAIT_WRITE_RANDOM_ADDR:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Setting TX power to 0 dBm...')
            self.ble_channel.aci_hal_set_tx_power_level(True, 0x19)
            self.state = self.WAIT_SET_TX_POWER_LEVEL

        elif self.state == self.WAIT_SET_TX_POWER_LEVEL:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Initializing GATT...')
            self.ble_channel.aci_gatt_init()
            self.state = self.WAIT_GATT_INIT

        elif self.state == self.WAIT_GATT_INIT:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Initializing GAP...')
            self.ble_channel.aci_gap_init(0x01, False, DEV_NAME)
            self.state = self.WAIT_GAP_INIT

        elif self.state == self.WAIT_GAP_INIT:
            assert event.payload[0]   == 0
            assert len(event.payload) == 7
            (gap_service_handle,
             dev_name_char_handle,
             appearance_char_handle) = struct.unpack('<xHHH', event.payload)
            self.gap_service     = gatt.Service(self.ble_channel,
                                                gap_service_handle)
            self.dev_name_char   = gatt.Characteristic(self.gap_service,
                                                       dev_name_char_handle)
            self.appearance_char = gatt.Characteristic(self.gap_service,
                                                       appearance_char_handle)
            print('Setting device name "%s"...' % DEV_NAME)
            self.dev_name_char.update_value(DEV_NAME)
            self.state = self.WAIT_SET_DEVICE_NAME

        elif self.state == self.WAIT_SET_DEVICE_NAME:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Setting device appearance...')
            self.appearance_char.update_value(DEV_APPEARANCE)
            self.state = self.WAIT_SET_DEVICE_APPEARANCE

        elif self.state == self.WAIT_SET_DEVICE_APPEARANCE:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Adding PSDB service...')
            self.ble_channel.aci_gatt_add_service(PSDB_UUID, 4)
            self.state = self.WAIT_ADD_PSDB_SERVICE

        elif self.state == self.WAIT_ADD_PSDB_SERVICE:
            assert event.payload[0]   == 0
            assert len(event.payload) == 3
            service_handle = struct.unpack_from('<H', event.payload, 1)[0]
            self.psdb_service = gatt.Service(self.ble_channel, service_handle)
            print('Adding PSDB characteristic...')
            self.psdb_service.add_char(PSDB_CHAR, 1, 0x02)
            self.state = self.WAIT_ADD_PSDB_CHAR

        elif self.state == self.WAIT_ADD_PSDB_CHAR:
            assert event.payload[0]   == 0
            assert len(event.payload) == 3
            char_handle = struct.unpack_from('<H', event.payload, 1)[0]
            self.psdb_char = gatt.Characteristic(self.psdb_service, char_handle)
            print('Updating PSDB characteristic...')
            self.psdb_char.update_value(struct.pack('<B', self.psdb_value))
            self.state = self.WAIT_UPDATE_PSDB_CHAR

        elif self.state == self.WAIT_UPDATE_PSDB_CHAR:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Setting default PHY...')
            self.ble_channel.hci_le_set_default_phy(0x00, 0x02, 0x02)
            self.state = self.WAIT_SET_DEFAULT_PHY

        elif self.state == self.WAIT_SET_DEFAULT_PHY:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Setting IO capability...')
            self.ble_channel.aci_gap_set_io_capability(0x01)
            self.state = self.WAIT_SET_IO_CAPABILITY

        elif self.state == self.WAIT_SET_IO_CAPABILITY:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Setting authentication requirements...')
            self.ble_channel.aci_gap_set_authentication_requirement(
                0, 0, 1, 0, 8, 16, 0, 111111, 0)
            self.state = self.WAIT_SET_AUTH_REQUIREMENT

        elif self.state == self.WAIT_SET_AUTH_REQUIREMENT:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            print('Starting advertising...')
            self.ble_channel.aci_gap_set_discoverable(0x00, 0x80, 0xA0, 0, 0,
                                                      LOCAL_NAME, [], 0, 0)
            self.state = self.WAIT_SET_DISCOVERABLE

        elif self.state == self.WAIT_SET_DISCOVERABLE:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            self.state = self.WAIT_EVENTS

        elif self.state == self.WAIT_INCREMENT_PSDB_CHAR:
            assert event.payload[0]   == 0
            assert len(event.payload) == 1
            self.state = self.WAIT_EVENTS

        else:
            raise Exception('Unexpected COMMAND_COMPLETE event! %s' % event)

    def handle_tick(self):
        if self.state != self.WAIT_EVENTS:
            return

        self.psdb_value += 1
        self.psdb_char.update_value(struct.pack('<B', self.psdb_value))
        self.state = self.WAIT_INCREMENT_PSDB_CHAR


def gen_manuf_data(client, mac_addr):
    data = struct.pack('<BBBBBBBB6B',
                       13, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
                       mac_addr[0], mac_addr[1], mac_addr[2],
                       mac_addr[3], mac_addr[4], mac_addr[5])
    assert len(data) == 14
    return data


def ble_hci_gap_gatt_init(client):
    # target = client.ipc.target

    # # And.. the ST code writes the IR and ER keys again.
    # print('Re-writing IR key...')
    # client.ipc.ble_channel.aci_hal_write_config_data_ir(CFG_IR)
    # print('Re-writing ER key...')
    # client.ipc.ble_channel.aci_hal_write_config_data_er(CFG_ER)
    pass


def poll_loop(client):
    delegate = BLEDelegate(client)
    delegate.start()

    t0 = time.time()
    while RUNNING:
        client.poll(timeout=0.01)
        if time.time() - t0 >= TICK_PERIOD_SEC:
            delegate.handle_tick()
            t0 = time.time()

    return

    # print('Reading local version information...')
    # client.ipc.ble_channel.hci_read_local_version_information()

    # print('Reading BD Addr...')
    # client.ipc.ble_channel.hci_read_bd_addr()

    # print('Looping on BLE events...')
    # while RUNNING:
    #     client.ipc.ble_channel.wait_and_pop_all_events(timeout=1)
    #     psdb_value = (psdb_value + 1) & 0xFF
    #     psdb_char.update_value(struct.pack('<B', psdb_value))


def main(rv):
    global RUNNING

    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        for p in psdb.probes.PROBES:
            p.show_info()

    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.find_default(usb_path=rv.usb_path)
    f     = probe.set_tck_freq(rv.probe_freq)
    print('Probing with SWD frequency at %.3f MHz' % (f/1.e6))

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose, connect_under_reset=True)

    # Use the best clock frequency.
    f      = target.set_max_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Flash and IPCC info.
    print('       Flash size: %u' % target.flash.flash_size)
    print('Flash sector size: %u' % target.flash.sector_size)
    print('IPCC mailbox addr: 0x%08X' % target.flash.get_ipccdba())

    # Start the existing CPU2 firmware and get a client object to interact with
    # it.
    target, client = target.ipc.start_firmware()

    # Switch to wireless firmware if necessary.
    if client.fw_name == 'FUS':
        print('Switching to wireless firmware...')
        target, client = client.start_ws_firmware()

    # Configure system clocks for RF firmware.
    target.configure_rf_clocks()

    # Ensure we are running BLE firmware.
    client.print_ws_version()
    assert client.fw_name == 'BLE Standard'

    # Loop forever.
    thread = threading.Thread(target=poll_loop, args=(client,))
    thread.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        RUNNING = False
        print()
        print('Quitting...')
        thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)
