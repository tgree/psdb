# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.


class STBinary(object):
    def __init__(self, fname, version, md5sum, addr_1M, addr_640K, addr_512K,
                 addr_256K):
        super(STBinary, self).__init__()
        self.fname     = fname
        self.version   = version
        self.md5sum    = md5sum
        self.addr      = {0x00100000 : addr_1M,
                          0x000A0000 : addr_640K,
                          0x00080000 : addr_512K,
                          0x00040000 : addr_256K,
                          }
        self.version_str = ('%u.%u.%u' % ((version >> 24) & 0xFF,
                                          (version >> 16) & 0xFF,
                                          (version >>  8) & 0xFF))


# Note: The FUS v1.1.0 binary that ships with the v1.5.0 GitHub release is bad
#       (missing footers and stuff - possibly not encrypted or packaged
#       correctly by ST) and you need to get the one from the v1.6.0 GitHub
#       release.
FUS_BINARIES = [
    # 1.2.0 - depending on whether or not we are coming from an 0.5.3 binary
    #         we must use one or the other.
    STBinary('stm32wb5x_FUS_fw_for_fus_0_5_3.bin', 0x01020000,
             'baf65bf930860ed2d4607609b8ce80df',
             0x080EC000, 0x0809A000, 0x0807A000, 0x0803A000),
    STBinary('stm32wb5x_FUS_fw.bin', 0x01020000,
             '06dbb3c9a003796470cd339d58523827',
             0x080EC000, 0x0809A000, 0x0807A000, 0x0803A000),
    ]
FUS_BINARY_LATEST = FUS_BINARIES[-1]
FUS_BINARY_UPGRADE_TABLE = {
    0x00050300 : FUS_BINARIES[0],
    }


WS_BINARIES = [
    # 1.13.3 series.
    STBinary('stm32wb5x_BLE_HCILayer_extended_fw.bin', 0x010D0302,
             'b8c1056914f5b39e2fd3e93c5528e55a',
             0x080DC000, 0x08088000, 0x08068000, 0x08028000),
    STBinary('stm32wb5x_BLE_HCILayer_fw.bin', 0x010D0302,
             '0df73a41d366861bc68e95a3b16e1dbe',
             0x080DC000, 0x08088000, 0x08068000, 0x08028000),
    STBinary('stm32wb5x_BLE_HCI_AdvScan_fw.bin', 0x010D0302,
             '81f34c0ed7cafc9523a26e833b2bd933',
             0x080EB000, 0x08097000, 0x08077000, 0x08037000),
    STBinary('stm32wb5x_BLE_LLD_fw.bin', 0x010C0002,
             'ff991aad1dd70d56c0a88bd4218cc452',
             0x080ED000, 0x08099000, 0x08079000, 0x08039000),
    STBinary('stm32wb5x_BLE_Mac_802_15_4_fw.bin', 0x010D0300,
             'e0e3878c2d4a23feb34126f4db3a6058',
             0x080B1000, 0x0805D000, 0x0803D000, None),
    STBinary('stm32wb5x_BLE_Stack_basic_fw.bin', 0x010D0302,
             'ff32be072fd9550e9bee0ab909ffe855',
             0x080D0000, 0x0807C000, 0x0805C000, 0x0801C000),
    STBinary('stm32wb5x_BLE_Stack_full_fw.bin', 0x010D0302,
             '36d01af43f161954184d3cdd916d3828',
             0x080D0000, 0x0807C000, 0x0805C000, 0x0801C000),
    STBinary('stm32wb5x_BLE_Stack_light_fw.bin', 0x010D0302,
             'a909c83418f8748854953355b9b833c7',
             0x080D7000, 0x08083000, 0x08063000, 0x08023000),
    STBinary('stm32wb5x_BLE_Thread_dynamic_fw.bin', 0x010C0001,
             '68bcda2e12d1c58a8852dd173a870ba4',
             0x0806D000, 0x08019000, None, None),
    STBinary('stm32wb5x_BLE_Thread_static_fw.bin', 0x010C0001,
             '1db89dfcabdc79a6d6cbbfe23fd150a1',
             0x0806F000, 0x0801B000, None, None),
    STBinary('stm32wb5x_BLE_Zigbee_FFD_dynamic_fw.bin', 0x010D0300,
             'f8b6132caf30168dcbf3665eff0c3c47',
             0x08071000, 0x0801D000, None, None),
    STBinary('stm32wb5x_BLE_Zigbee_FFD_static_fw.bin', 0x010D0200,
             'c1392e5d1a863f915f3d5892976a964e',
             0x08073000, 0x0801F000, None, None),
    STBinary('stm32wb5x_BLE_Zigbee_RFD_dynamic_fw.bin', 0x010D0300,
             'e9510bd126e86f36d8dd3772378155a1',
             0x08080000, 0x0802C000, 0x0800C000, None),
    STBinary('stm32wb5x_BLE_Zigbee_RFD_static_fw.bin', 0x010D0200,
             'c11cd164f2f59a5d139537b29c7183bb',
             0x08081000, 0x0802D000, 0x0800D000, None),
    STBinary('stm32wb5x_Mac_802_15_4_fw.bin', 0x010D0000,
             '93c1924c52a1493e4e9c00e6cac1bced',
             0x080E3000, 0x0808F000, 0x0806F000, 0x0802F000),
    STBinary('stm32wb5x_Phy_802_15_4_fw.bin', 0x010D0001,
             '434c924682c7cac628ab0bd1c50774c1',
             0x080DE000, 0x0808A000, 0x0806A000, 0x0802A000),
    STBinary('stm32wb5x_Thread_FTD_fw.bin', 0x010D0000,
             '55fb3109fd5f3fe392bb11786677631b',
             0x08097000, 0x08043000, 0x08023000, None),
    STBinary('stm32wb5x_Thread_MTD_fw.bin', 0x010D0000,
             '1465653f815c11c8bf55f39ddc47ae34',
             0x080AA000, 0x08056000, 0x08036000, None),
    STBinary('stm32wb5x_Thread_RCP_fw.bin', 0x010D0000,
             '68be9620adf0dabe7eef3faaccf8e750',
             0x080DA000, 0x08086000, 0x08066000, 0x08026000),

    # This guys blew up my Nucleo-WB55.  There was no warning about it in the
    # release notes.  The SRAM2a area is limited to 4K on these firmwares and
    # we normally try to use a larger layout including an MM BLE Pool of 2048
    # bytes.  To recover from this firmware:
    #
    #   1. In mailbox.py change the following lines to use lengths of 512
    #      instead of 2048:
    #
    #      self.mm_ble_pool_len              = 512
    #      assert self.ram_size >= 0xE00 + 512
    #
    #   2. Delete the firmware using fus_tool:
    #
    #      python3 -m psdb.fus_tool -v --fw-delete
    #
    #   3. Revert the mailbox.py changes.
    #
    # Alternatively, we should see if we our code always works with a smaller
    # 512-byte MM BLE Pool.
    STBinary('stm32wb5x_Zigbee_FFD_fw.bin', 0x010D0200,
             'f3d3acb101d713ebac41f32f2cff03c1',
             0x080A4000, 0x08050000, 0x08030000, None),
    STBinary('stm32wb5x_Zigbee_RFD_fw.bin', 0x010D0200,
             'b63ef7a26b459eee97402886fb66ac61',
             0x080B2000, 0x0805E000, 0x0803E000, None),

    # This guy blew up my Nucleo-WB55, and after flashing it I looked at the
    # warning in the release notes...  To recover it:
    #
    #   1. In mailbox.py change the base addresses of the following items:
    #
    #      self.ble_hci_acl_data_buffer_addr = self.base_addr + 0x8800
    #      self.mm_ble_buffer_addr           = self.base_addr + 0x8A00
    #      self.mm_sys_buffer_addr           = self.base_addr + 0x8C00
    #      self.mm_ble_pool_addr             = self.base_addr + 0x8E00
    #
    #   2. In mailbox.py, comment out the following line:
    #
    #      #assert self.ram_size >= 0xE00 + 2048
    #
    #   3. Delete the firmware using fus_tool:
    #
    #      python3 -m psdb.fus_tool -v --fw-delete
    #
    #   4. Revert the changes and avoid this binary again!
    STBinary('stm32wb5x_BLE_Stack_full_extended_fw.bin', 0x010D0302,
             'e799fc3338ff356b44ad73f107c990b1',
             0x080C7000, 0x08073000, 0x08053000, 0x08013000),
    ]


def find_fus_binary(current_version):
    return FUS_BINARY_UPGRADE_TABLE.get(current_version, FUS_BINARY_LATEST)


def find_ws_binary(md5sum):
    for wb in WS_BINARIES:
        if wb.md5sum == md5sum:
            return wb
    raise Exception('WS binary with MD5 %s not found.' % md5sum)
