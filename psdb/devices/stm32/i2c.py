# Copyright (c) 2023-2024 by Phase Advanced Sensor Systems, Inc.
import time

from ..device import Device, AReg32


class NACKException(Exception):
    pass


class I2C(Device):
    '''
    Driver for generic STM32 I2C peripheral.
    '''
    REGS = [AReg32('CR1',       0x00,  [('PE',              0),
                                        ('TXIE',            1),
                                        ('RXIE',            2),
                                        ('ADDRIE',          3),
                                        ('NACKIE',          4),
                                        ('STOPIE',          5),
                                        ('TCIE',            6),
                                        ('ERRIE',           7),
                                        ('DNF',             8,  11),
                                        ('ANFOFF',          12),
                                        ('TXDMAEN',         14),
                                        ('RXDMAEN',         15),
                                        ('SBC',             16),
                                        ('NOSTRETCH',       17),
                                        ('WUPEN',           18),
                                        ('GCEN',            19),
                                        ('SMBHEN',          20),
                                        ('SMBDEN',          21),
                                        ('ALERTEN',         22),
                                        ('PECEN',           23),
                                        ]),
            AReg32('CR2',       0x04,  [('SADD',            0,  9),
                                        ('RD_WRN',          10),
                                        ('ADD10',           11),
                                        ('HEAD10R',         12),
                                        ('START',           13),
                                        ('STOP',            14),
                                        ('NACK',            15),
                                        ('NBYTES',          16, 23),
                                        ('RELOAD',          24),
                                        ('AUTOEND',         25),
                                        ('PECBYTE',         26),
                                        ]),
            AReg32('OAR1',      0x08,  [('OA1',             0,  9),
                                        ('OA1MODE',         10),
                                        ('OA1EN',           15),
                                        ]),
            AReg32('OAR2',      0x0C,  [('OA2',             0,  7),
                                        ('OA2MSK',          9,  10),
                                        ('OA2EN',           15),
                                        ]),
            AReg32('TIMINGR',   0x10,  [('SCLL',            0,  7),
                                        ('SCLH',            8,  15),
                                        ('SDADEL',          16, 19),
                                        ('SCLDEL',          20, 23),
                                        ('PRESC',           28, 31),
                                        ]),
            AReg32('TIMEOUTR',  0x14,  [('TIMEOUTA',        0,  11),
                                        ('TIDLE',           12),
                                        ('TIMOUTEN',        15),
                                        ('TIMEOUTB',        16, 27),
                                        ('TEXTEN',          31),
                                        ]),
            AReg32('ISR',       0x18,  [('TXE',             0),
                                        ('TXIS',            1),
                                        ('RXNE',            2),
                                        ('ADDR',            3),
                                        ('NACKF',           4),
                                        ('STOPF',           5),
                                        ('TC',              6),
                                        ('TCR',             7),
                                        ('BERR',            8),
                                        ('ARLO',            9),
                                        ('OVR',             10),
                                        ('PECERR',          11),
                                        ('TIMEOUT',         12),
                                        ('ALERT',           13),
                                        ('BUSY',            15),
                                        ('DIR',             16),
                                        ('ADDCODE',         17, 23),
                                        ]),
            AReg32('ICR',       0x1C,  [('ADDRCF',          3),
                                        ('NACKCF',          4),
                                        ('STOPCF',          5),
                                        ('BERRCF',          8),
                                        ('ARLOCF',          9),
                                        ('OVRCF',           10),
                                        ('PECCF',           11),
                                        ('TIMOUTCF',        12),
                                        ('ALERTCF',         13),
                                        ]),
            AReg32('PECR',      0x20,  [('PEC',             0,  7),
                                        ]),
            AReg32('RXDR',      0x24,  [('RXDATA',          0,  7),
                                        ]),
            AReg32('TXDR',      0x28,  [('TXDATA',          0,  7), ]),
            ]

    def __init__(self, target, ap, name, addr, regs=None, **kwargs):
        super().__init__(target, ap, addr, name, regs or I2C.REGS, **kwargs)

    def i2c_read(self, addr7, nbytes):
        assert nbytes < 256

        # Start the read operation.
        self._CR2 = ((addr7  <<  1) |
                     (1      << 10) |
                     (nbytes << 16) |
                     (1      << 25) |
                     (1      << 13))

        # We will get either NACKF (if no such slave address exists) or RXNE.
        data = b''
        while nbytes:
            retries = 0
            isr = self._ISR.read()
            if isr & (1 << 4):
                self._ICR = (1 << 4)
                raise NACKException()
            if isr & (1 << 2):
                data    = data + bytes([self._RXDR.RXDATA])
                nbytes -= 1
                retries = 0
                continue

            retries += 1
            if retries >= 1000:
                raise Exception('Timed out waiting for RX data!')
            time.sleep(0.0001)

        return data

    def i2c_write(self, addr7, data):
        nbytes = len(data)
        assert nbytes < 256

        # Start the write operation.
        self._CR2 = ((addr7  <<  1) |
                     (nbytes << 16) |
                     (1      << 25) |
                     (1      << 13))

        # We will get either NACKF (if no such slave address exists or if the
        # slave terminated the transfer) or TXIS.
        while nbytes:
            retries = 0
            isr = self._ISR.read()
            if isr & (1 << 4):
                self._ICR = (1 << 4)
                if nbytes == len(data):
                    raise NACKException()
                else:
                    break
            if isr & (1 << 1):
                self._TXDR = data[len(data) - nbytes]
                nbytes    -= 1
                retries    = 0
                continue

            retries += 1
            if retries >= 1000:
                raise Exception('Timed out waiting to TX data!')
            time.sleep(0.0001)
