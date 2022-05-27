# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import math
import struct

from psdb.devices import Device, Reg8S, Reg32S, AReg32


class QUADSPI(Device):
    '''
    Driver for the STM32 quad-SPI peripheral found on many MCUs (QUADSPI).
    '''
    REGS = [AReg32('CR',        0x000, [('EN',           0),
                                        ('ABORT',        1),
                                        ('DMAEN',        2),
                                        ('TCEN',         3),
                                        ('SSHIFT',       4),
                                        ('DFM',          6),
                                        ('FSEL',         7),
                                        ('FTHRES',       8, 11),
                                        ('TEIE',        16),
                                        ('TCIE',        17),
                                        ('FTIE',        18),
                                        ('SMIE',        19),
                                        ('TOIE',        20),
                                        ('APMS',        22),
                                        ('PMM',         23),
                                        ('PRESCALER',   24, 31),
                                        ]),
            AReg32('DCR',       0x004, [('CKMODE',       0),
                                        ('CSHT',         8, 10),
                                        ('FSIZE',       16, 20),
                                        ]),
            AReg32('SR',        0x008, [('TEF',          0),
                                        ('TCF',          1),
                                        ('FTF',          2),
                                        ('SMF',          3),
                                        ('TOF',          4),
                                        ('BUSY',         5),
                                        ('FLEVEL',       8, 12),
                                        ]),
            AReg32('FCR',       0x00C, [('CTEF',         0),
                                        ('CTCF',         1),
                                        ('CSMF',         3),
                                        ('CTOF',         4),
                                        ]),
            AReg32('DLR',       0x010, [('DL',           0, 31),
                                        ]),
            AReg32('CCR',       0x014, [('INSTRUCTION',  0,  7),
                                        ('IMODE',        8,  9),
                                        ('AMODE',       10, 11),
                                        ('ADSIZE',      12, 13),
                                        ('ABMODE',      14, 15),
                                        ('ABSIZE',      16, 17),
                                        ('DCYC',        18, 22),
                                        ('DMODE',       24, 25),
                                        ('FMODE',       26, 27),
                                        ('SIOO',        28),
                                        ('DHHC',        30),
                                        ('DDRM',        31),
                                        ]),
            AReg32('AR',        0x018, [('ADDRESS',      0, 31),
                                        ]),
            AReg32('ABR',       0x01C, [('ALTERNATE',    0, 31),
                                        ]),
            Reg8S('DR8',        0x020),
            Reg32S('DR32',      0x020),
            AReg32('PSMKR',     0x024, [('MASK',         0, 31),
                                        ]),
            AReg32('PSMAR',     0x028, [('MATCH',        0, 31),
                                        ]),
            AReg32('PIR',       0x02C, [('INTERVAL',     0, 15),
                                        ]),
            AReg32('LPTR',      0x030, [('TIMEOUT',      0, 15),
                                        ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, QUADSPI.REGS, **kwargs)

    def set_flash_size(self, nbytes):
        '''
        Sets the target flash size and ensures the QSPI peripheral enable bit
        is on.  The target flash size needs to be set to a non-zero value
        before command that read  more than one byte of data can be executed.
        '''
        nbytes_log2     = math.ceil(math.log(nbytes, 2))
        self._CR.EN     = 1
        self._DCR.FSIZE = nbytes_log2 - 1

    def _wait_wip_clear(self):
        while (self.read_status_register() & (1 << 0)):
            pass

    def _exec_command(self, cmd, addr=None):
        self._CR.FTHRES = 0
        self._DLR       = 0
        self._CCR       = cmd
        if addr is not None:
            self._AR = addr

        while self._SR.TCF == 0:
            pass
        self._FCR.CTCF = 1

    def _exec_input_command(self, cmd, nbytes, addr=None):
        fthresh         = min(nbytes, 16)
        self._CR.FTHRES = fthresh - 1
        self._DLR       = nbytes - 1
        self._CCR       = cmd
        if addr is not None:
            self._AR = addr

        data = b''
        while nbytes >= 4:
            while self._SR.FLEVEL < 4:
                pass

            v       = self._DR32.read()
            data   += struct.pack('<I', v)
            nbytes -= 4

        while nbytes:
            while self._SR.FLEVEL == 0:
                pass

            v       = self._DR8.read()
            data   += struct.pack('<B', v)
            nbytes -= 1

        sr = self._SR.read()
        assert sr == 0x00000002
        self._FCR.CTCF = 1

        return data

    def _exec_output_command(self, cmd, data, addr=None):
        self._CR.FTHRES = 3
        self._DLR       = len(data) - 1
        self._CCR       = cmd
        if addr is not None:
            self._AR = addr

        rem = len(data)
        while rem >= 4:
            while self._SR.FTF == 0:
                pass

            self._DR32 = struct.unpack_from('<I', data,
                                            offset=len(data) - rem)[0]
            rem       -= 4

        while rem:
            while self._SR.FTF == 0:
                pass

            self._DR8 = data[-rem]
            rem      -= 1

        assert self._SR.TCF == 1
        self._FCR.CTCF = 1

    def release_from_power_down_read_dev_id(self):
        '''
        Issue the RES (0xAB) command.  This releases the device from power-
        down if it was in the power-down state and it also returns a device-ID
        value.
        '''
        data = self._exec_input_command(0x056001AB, 1)
        return data[0]

    def read_identification(self):
        '''
        Issue the RDID (0x9F) command.  This reads the 3-byte JEDEC ID
        sequence:

        +----------------+---------------------------------+
        |   Manuf. ID    |            Device ID            |
        +----------------+---------------------------------+
        '''
        data       = self._exec_input_command(0x0500019F, 3)
        m_id, d_id = struct.unpack('>BH', data)
        return m_id, d_id

    def write_enable(self):
        '''
        Issue the WREN (0x06) command to enable write operations.
        '''
        self._exec_command(0x00000106)

    def write_disable(self):
        '''
        Issue the WRDI (0x04) command to disable write operations.
        '''
        self._exec_command(0x00000104)

    def read_status_register(self):
        '''
        Issue the RDSR (0x05) command to read the flash status register.
        '''
        data = self._exec_input_command(0x05000105, 1)
        return data[0]

    def write_status_register(self, v):
        '''
        Issue the WRSR (0x01) command to write the flash status register.
        '''
        self._exec_output_command(0x01000101, struct.pack('<B', v))

    def quad_read_24(self, addr, nbytes):
        '''
        Issue the FRQO (0x6B) command to read from the specified 24-bit address
        in flash.
        '''
        return self._exec_input_command(0x0720256B, nbytes, addr=addr)

    def quad_write_24(self, addr, data):
        '''
        Issue the PPQ (0x32) command to write data to the specified 24-bit
        address in flash.  The data must not cross a 256-byte coundary.
        '''
        self.write_enable()
        self._exec_output_command(0x03002532, data, addr=addr)
        self._wait_wip_clear()

    def sector_erase(self, addr):
        '''
        Issue the SER (0x20) command to erase the specified 4K sector in flash.
        '''
        self.write_enable()
        self._exec_command(0x00002520, addr=addr)
        self._wait_wip_clear()

    def block_erase_32K(self, addr):
        '''
        Issue the BER32K (0x52) command to erase the specified 32K sector in
        flash.
        '''
        self.write_enable()
        self._exec_command(0x00002552, addr=addr)
        print('Erase in progress...')
        self._wait_wip_clear()

    def block_erase_64K(self, addr):
        '''
        Issue the BER64K (0xD8) command to erase the specified 64K sector in
        flash.
        '''
        self.write_enable()
        self._exec_command(0x000025D8, addr=addr)
        print('Erase in progress...')
        self._wait_wip_clear()

    def chip_erase(self):
        '''
        Issue the CER (0x60) command to erase the entire flash.
        '''
        self.write_enable()
        self._exec_command(0x00000160)
        print('Erase in progress...')
        self._wait_wip_clear()
