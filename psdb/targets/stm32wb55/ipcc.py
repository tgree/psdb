# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from ..device import Device, Reg32
import time


class TimeoutError(Exception):
    pass


class IPCC(Device):
    '''
    Driver for the STM Inter-Processor Communication Controller (IPCC) device.
    '''
    REGS = [Reg32('C1CR',       0x00,  [('RXOIE',       1),
                                        ('',            15),
                                        ('TXFIE',       1),
                                        ]),
            Reg32('C1MR',       0x04,  [('CH1OM',       1),
                                        ('CH2OM',       1),
                                        ('CH3OM',       1),
                                        ('CH4OM',       1),
                                        ('CH5OM',       1),
                                        ('CH6OM',       1),
                                        ('',            10),
                                        ('CH1FM',       1),
                                        ('CH2FM',       1),
                                        ('CH3FM',       1),
                                        ('CH4FM',       1),
                                        ('CH5FM',       1),
                                        ('CH6FM',       1),
                                        ]),
            Reg32('C1SCR',      0x08,  [('CH1C',        1),
                                        ('CH2C',        1),
                                        ('CH3C',        1),
                                        ('CH4C',        1),
                                        ('CH5C',        1),
                                        ('CH6C',        1),
                                        ('',            10),
                                        ('CH1S',        1),
                                        ('CH2S',        1),
                                        ('CH3S',        1),
                                        ('CH4S',        1),
                                        ('CH5S',        1),
                                        ('CH6S',        1),
                                        ]),
            Reg32('C1TOC2SR',   0x0C,  [('CH1F',        1),
                                        ('CH2F',        1),
                                        ('CH3F',        1),
                                        ('CH4F',        1),
                                        ('CH5F',        1),
                                        ('CH6F',        1),
                                        ]),
            Reg32('C2CR',       0x10,  [('RXOIE',       1),
                                        ('',            15),
                                        ('TXFIE',       1),
                                        ]),
            Reg32('C2MR',       0x14,  [('CH1OM',       1),
                                        ('CH2OM',       1),
                                        ('CH3OM',       1),
                                        ('CH4OM',       1),
                                        ('CH5OM',       1),
                                        ('CH6OM',       1),
                                        ('',            10),
                                        ('CH1FM',       1),
                                        ('CH2FM',       1),
                                        ('CH3FM',       1),
                                        ('CH4FM',       1),
                                        ('CH5FM',       1),
                                        ('CH6FM',       1),
                                        ]),
            Reg32('C2SCR',      0x18,  [('CH1C',        1),
                                        ('CH2C',        1),
                                        ('CH3C',        1),
                                        ('CH4C',        1),
                                        ('CH5C',        1),
                                        ('CH6C',        1),
                                        ('',            10),
                                        ('CH1S',        1),
                                        ('CH2S',        1),
                                        ('CH3S',        1),
                                        ('CH4S',        1),
                                        ('CH5S',        1),
                                        ('CH6S',        1),
                                        ]),
            Reg32('C2TOC1SR',   0x1C,  [('CH1F',        1),
                                        ('CH2F',        1),
                                        ('CH3F',        1),
                                        ('CH4F',        1),
                                        ('CH5F',        1),
                                        ('CH6F',        1),
                                        ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(IPCC, self).__init__(target, ap, addr, name, IPCC.REGS, **kwargs)

    def set_tx_flag(self, channel):
        '''
        Set the CPU1 transmit status flag for the specified channel.  This will
        generate an RX-occupied interrupt on CPU2.  The channel number is 1-
        based.
        '''
        assert channel and channel <= 6
        self._C1SCR = (1 << (16 + channel - 1))

    def get_tx_free_flag(self, channel):
        '''
        Returns True if the CPU1 TX-free flag is set for the specified channel.
        The channel number is 1-based.
        '''
        return (self._C1TOC2SR.read() & (1 << (channel - 1))) == 0

    def clear_rx_flag(self, channel):
        '''
        Clear the CPU1 receive status flag for the specified channel.  This
        will generate a TX-free interrupt on CPU2.  The channel number is 1-
        based.
        '''
        assert channel and channel <= 6
        self._C1SCR = (1 << (channel - 1))

    def get_rx_flag(self, channel):
        '''
        Returns True if the CPU1 RX-occupied flag is set for the specified
        channel.  The channel number is 1-based.
        '''
        return (self._C2TOC1SR.read() & (1 << (channel - 1))) != 0

    def wait_tx_free(self, channel, timeout=None):
        '''
        Waits until the specified CPU1 transmit channel becomes free,
        indicating that new data can be written for transfer to CPU2.  The
        channel number is 1-based.
        '''
        timeout = 1000000000 if timeout is None else timeout
        t0      = time.time()
        while time.time() - t0 < timeout and not self.get_tx_free_flag(channel):
            time.sleep(0.001)
        if not self.get_tx_free_flag(channel):
            raise TimeoutError('Timed out waiting for TX free flag')

    def wait_rx_occupied(self, channel, timeout=None):
        '''
        Waits until the specified CPU1 receive channel becomes occupied,
        indicating that new data is available for transfer from CPU2.  The
        channel number is 1-based.
        '''
        timeout = 1000000000 if timeout is None else timeout
        t0      = time.time()
        while time.time() - t0 < timeout and not self.get_rx_flag(channel):
            time.sleep(0.001)
        if not self.get_rx_flag(channel):
            raise TimeoutError('Timed out waiting for RX occupied flag')
