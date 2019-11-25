# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from . import bd


class RAMBD(bd.BlockDevice):
    '''
    Implements a sparse RAM block device.  Only blocks to which data has been
    written will be populated in the RAMBD.blocks dict which is addressed by
    block number.
    '''
    def __init__(self, block_size, first_block=0, nblocks=0x10000000000000000):
        super(RAMBD, self).__init__(block_size, b'\xff')
        self.blocks      = {}
        self.first_block = first_block
        self.end_block   = first_block + nblocks

    def write(self, addr, data):
        block_size = len(self.fill)

        while data:
            avail    = block_size - (addr % block_size)
            count    = min(len(data), avail)
            blocknum = addr // block_size
            if blocknum < self.first_block or blocknum >= self.end_block:
                raise bd.BlockOutOfRangeException(self, blocknum)

            blockaddr = blocknum*block_size
            block     = self.blocks.get(blocknum,
                                        bd.Block(blockaddr, self.fill))
            block.write(addr, data[:count])

            self.blocks[blocknum] = block
            data                  = data[count:]
            addr                 += count
