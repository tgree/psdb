#!/usr/bin/env python3
# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import psdb.probes
import psdb.targets
from psdb.util import hexify

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


def gen_manuf_data(client, mac_addr):
    data = struct.pack('<BBBBBBBB6B',
                       13, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
                       mac_addr[0], mac_addr[1], mac_addr[2],
                       mac_addr[3], mac_addr[4], mac_addr[5])
    assert len(data) == 14
    return data


def ble_hci_gap_gatt_init(client):
    target = client.ipc.target

    # HCI reset to sync the BLE stack.
    print('Resetting HCI...')
    rsp = client.ipc.ble_channel.hci_reset()
    assert len(rsp) == 1
    assert rsp[0].payload == b'\x00'

    # Read config BD addr.
    print('Reading CONFIG_DATA_PUBADDR...')
    rsp = client.ipc.ble_channel.aci_hal_read_config_data_pubaddr()
    print('PUBADDR: %s' % hexify(rsp))

    # Read IR key.
    print('Reading IR key...')
    rsp = client.ipc.ble_channel.aci_hal_read_config_data_ir()
    print('IRK: %s' % hexify(rsp))

    # Read ER key.
    print('Reading ER key...')
    rsp = client.ipc.ble_channel.aci_hal_read_config_data_er()
    print('ERK: %s' % hexify(rsp))

    # Read the static random address.
    print('Reading static random address...')
    rsp = client.ipc.ble_channel.aci_hal_read_config_data_random_address()
    print('RA: %s' % hexify(rsp))

    # Write the generated UDN BD addr.
    print('Writing UDN-generated public address...')
    client.ipc.ble_channel.aci_hal_write_config_data_pubaddr(
            target.ble_mac_addr)

    # Write the identity root key.
    print('Writing IR key...')
    client.ipc.ble_channel.aci_hal_write_config_data_ir(CFG_IR)

    # Write the encryption root key.
    print('Writing ER key...')
    client.ipc.ble_channel.aci_hal_write_config_data_er(CFG_ER)

    # Write a static random address.  The comments in the ST code indicate that
    # the "two upper bits shall be set to 1" but unless there is some amazing
    # byte-swapping going on here, this code doesn't do that.
    print('Writing static random address...')
    rand_addr = struct.pack('<LH', target.uid64_udn, 0xED6E)
    client.ipc.ble_channel.aci_hal_write_config_data_random_address(rand_addr)

    # And.. the ST code writes the IR and ER keys again.
    print('Re-writing IR key...')
    client.ipc.ble_channel.aci_hal_write_config_data_ir(CFG_IR)
    print('Re-writing ER key...')
    client.ipc.ble_channel.aci_hal_write_config_data_er(CFG_ER)

    # Set the TX power level to 0 dBm.
    print('Setting TX power to 0 dBm...')
    client.ipc.ble_channel.aci_hal_set_tx_power_level(True, 0x19)

    # Initialize GATT.
    print('Initializing GATT...')
    client.ipc.ble_channel.aci_gatt_init()

    # Initialize GAP.
    print('Initializing GAP...')
    (gap_service,
     dev_name_char,
     appearance_char) = client.ipc.ble_channel.aci_gap_init(0x01, False,
                                                            DEV_NAME)

    # Set device name.
    print('Setting device name "%s"...' % DEV_NAME)
    dev_name_char.update_value(DEV_NAME)

    # Set device appearance.
    print('Setting device appearance...')
    appearance_char.update_value(DEV_APPEARANCE)

    # Add our service.
    print('Adding PSDB service...')
    psdb_service = client.ipc.ble_channel.aci_gatt_add_service(PSDB_UUID, 4)

    # Add our characteristic.
    print('Adding PSDB characteristic...')
    psdb_char = psdb_service.add_char(PSDB_CHAR, 1, 0x02)

    # Initialize default phy.
    print('Setting default PHY...')
    client.ipc.ble_channel.hci_le_set_default_phy(0x00, 0x02, 0x02)

    # Set IO capability.
    print('Setting IO capability...')
    client.ipc.ble_channel.aci_gap_set_io_capability(0x01)

    # Set authentication requirements.
    print('Setting authentication requirements...')
    client.ipc.ble_channel.aci_gap_set_authentication_requirement(
        0, 0, 1, 0, 8, 16, 0, 111111, 0)

    return psdb_char


def adv_init(client):
    print('Starting advertising...')
    client.ipc.ble_channel.aci_gap_set_discoverable(0x00, 0x80, 0xA0, 0, 0,
                                                    LOCAL_NAME, [], 0, 0)


def poll_loop(client):
    print('Starting BLE firmware...')
    print(client.ipc.system_channel.exec_ble_init())

    psdb_value = 0
    psdb_char  = ble_hci_gap_gatt_init(client)
    psdb_char.update_value(struct.pack('<B', psdb_value))

    adv_init(client)

    print('Reading local version information...')
    client.ipc.ble_channel.hci_read_local_version_information()

    print('Reading BD Addr...')
    client.ipc.ble_channel.hci_read_bd_addr()

    print('Looping on BLE events...')
    while RUNNING:
        client.ipc.ble_channel.wait_and_pop_all_events(timeout=1)
        psdb_value = (psdb_value + 1) & 0xFF
        psdb_char.update_value(struct.pack('<B', psdb_value))


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
