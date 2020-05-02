#!/usr/bin/env python3
# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import psdb.probes
import psdb.targets

import argparse
import time
import sys


SUPPORTED_PLATFORMS = (
    psdb.targets.stm32wb55.STM32WB55,
    )


def main(rv):
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
    assert isinstance(target, SUPPORTED_PLATFORMS)

    # Use the best clock frequency.
    f      = target.set_max_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Flash and IPCC info.
    print('       Flash size: %u' % target.flash.flash_size)
    print('Flash sector size: %u' % target.flash.sector_size)
    print('IPCC mailbox addr: 0x%08X' % target.flash.get_ipccdba())

    # Attempt an entry into FUS.
    if rv.fus_enter or rv.fus_upgrade or rv.fw_delete or rv.fw_upgrade:
        print('Entering FUS mode...')
        target = target.ipc.start_fus_firmware()

    # Delete an existing firmware if requested.
    if rv.fw_delete:
        print('Deleting wireless firmware...')
        target = target.ipc.delete_ws_firmware()

    # Attempt a FUS upgrade.
    if rv.fus_upgrade:
        print('Upgrading FUS...')
        assert rv.bin_dir
        target = target.ipc.upgrade_fus_firmware(rv.bin_dir)

    # Attempt a WS firmare upgrade.
    if rv.fw_upgrade:
        print('Upgrading WS firmware...')
        target = target.ipc.upgrade_ws_firmware(rv.fw_upgrade)

    # Attempt an entry into wireless firmware.
    if rv.fw_enter:
        print('Entering wireless firmware...')
        target = target.ipc.start_ws_firmware()

    # Configure for booting into flash again.
    if rv.set_flash_boot:
        print('Setting to boot from flash...')
        target = target.flash.set_boot_flash(verbose=rv.verbose,
                                             connect_under_reset=True)
        target.resume()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--fus-enter', action='store_true')
    parser.add_argument('--fus-upgrade', action='store_true')
    parser.add_argument('--bin-dir')
    parser.add_argument('--fw-enter', action='store_true')
    parser.add_argument('--fw-delete', action='store_true')
    parser.add_argument('--fw-upgrade')
    parser.add_argument('--set-flash-boot', action='store_true')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)