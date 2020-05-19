#!/usr/bin/env python3
# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import psdb.probes
import psdb.targets

import argparse
import threading
import time
import sys


RUNNING = True


def poll_loop(client):
    print('Starting BLE firmware...')
    print(client.ipc.system_channel.exec_ble_init())

    print('Reading local version information...')
    client.ipc.ble_channel.hci_read_local_version_information()

    print('Reading BD Addr...')
    client.ipc.ble_channel.hci_read_bd_addr()

    print('Looping on BLE events...')
    while RUNNING:
        client.ipc.ble_channel.wait_and_pop_all_events(dump=True, timeout=1)


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

    # Use the probe to detect a target platform - it should be 
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
        thread.join()
        print()


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
