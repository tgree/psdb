# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.


class STBinary(object):
    def __init__(self, fname, version, md5sum, addr_1M, addr_512K, addr_256K):
        super(STBinary, self).__init__()
        self.fname     = fname
        self.version   = version
        self.md5sum    = md5sum
        self.addr      = {0x00100000 : addr_1M,
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
    # 1.0.2 - this can be installed on any STM32WB55 from 0.5.3; but you can't
    #         upgrade to it from 1.0.1 - you must go straight to 1.1.0.
    STBinary('stm32wb5x_FUS_fw_1_0_2.bin', 0x01000200,
             'e5c01503170dd68f4ff645073cb55bd9',
             0x080EC000, 0x0807A000, 0x0803A000),

    # 1.1.0 - this can be installed on any STM32WB55 that has either 1.0.1 or
    #         1.0.2 installed, but you can't go here straight from 0.5.3.  If
    #         you have 0.5.3 installed, you need to install 1.0.2 first.
    STBinary('stm32wb5x_FUS_fw.bin', 0x01010000,
             'f8c05283ed3cdae4cc11bd6afe6b2131',
             0x080EC000, 0x0807A000, 0x0803A000),
    ]
FUS_BINARY_LATEST = FUS_BINARIES[-1]


WS_BINARIES = [
    # 1.1.0 series.
    STBinary('stm32wb5x_rfmonitor_phy802_15_4_fw.bin', 0x01010000,
             'b4067bef8016dcf48685c4940c158752',
             0x080EC000, 0x08078000, 0x08038000),

    # 1.5.0 series.
    STBinary('stm32wb5x_BLE_Stack_full_fw.bin', 0x01050000,
             'af381ee93e812325542864acac6611e7',
             0x080CB000, 0x08057000, 0x08017000),

    # 1.6.0 series.
    # 1.7.0 series - identical to 1.6.0 but they changed th load addresses for
    #                the stm32wb5x_Thread_FTD_fw.bin binary.
    STBinary('stm32wb5x_BLE_HCILayer_fw.bin', 0x01060000,
             '2ebc328dc5c54b553578951a5ace5c8d',
             0x080DC000, 0x08068000, 0x08028000),
    STBinary('stm32wb5x_BLE_Stack_full_fw.bin', 0x01060000,
             '5a1bbd9af07fbef316abfe311d6b3675',
             0x080CB000, 0x08057000, 0x08017000),
    STBinary('stm32wb5x_BLE_Stack_light_fw.bin', 0x01060000,
             'ebedb5ded0c4834779254118409b21a1',
             0x080D9000, 0x08065000, 0x08025000),
    STBinary('stm32wb5x_BLE_Thread_fw.bin', 0x01060000,
             'ed510ab3ea7c778816546799b9f8f3b9',
             0x08078000, None, None),
    STBinary('stm32wb5x_BLE_Zigbee_FFD_static_fw.bin', 0x01060000,
             '9ceaf8d771b2e74594148c8ca397be8c',
             0x0807C000, None, None),
    STBinary('stm32wb5x_Mac_802_15_4_fw.bin', 0x01060000,
             '0229ca69cfc8ae3dd6541a34ee349025',
             0x080E4000, 0x08070000, 0x08030000),
    STBinary('stm32wb5x_Thread_FTD_fw.bin', 0x01060000,
             'a247ffad7858571e464a217b083e7f8f',
             0x0809E000, 0x0802A000, None),
    STBinary('stm32wb5x_Thread_MTD_fw.bin', 0x01060000,
             '68afe9bd5bf9a84fef096f3933d0ebe1',
             0x080B4000, 0x08040000, None),
    STBinary('stm32wb5x_Zigbee_FFD_Full_fw.bin', 0x01060000,
             '4efd24eb63a986d79dc4f00bfb0c8ba4',
             0x080A9000, 0x08035000, None),
    STBinary('stm32wb5x_Zigbee_RFD_fw.bin', 0x01060000,
             '884cc706ae9346581ee7e35a2f6b01c9',
             0x080B3000, 0x0803F000, None),
    ]


def find_fus_binary(version):
    for fb in FUS_BINARIES:
        if fb.version == version:
            return fb
    raise Exception('FUS binary with version 0x%08X not found.' % version)


def find_ws_binary(md5sum):
    for wb in WS_BINARIES:
        if wb.md5sum == md5sum:
            return wb
    raise Exception('WS binary with MD5 %s not found.' % md5sum)
