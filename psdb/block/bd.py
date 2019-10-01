# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.


class BlockOutOfRangeException(Exception):
    def __init__(self, bd, block_num):
        super(BlockOutOfRangeException, self).__init__(
              'Block %u out of range' % block_num)
        self.bd        = bd
        self.block_num = block_num


class Block(object):
    def __init__(self, addr, data):
        self.addr = addr
        self.data = data[:]

    def write(self, addr, data):
        assert self.addr <= addr
        assert addr + len(data) <= self.addr + len(self.data)

        addr    -= self.addr
        new_data = self.data[:addr] + data + self.data[addr + len(data):]
        assert len(new_data) == len(self.data)

        self.data = new_data


class BlockDevice(object):
    def __init__(self, block_size, fill=b'\xff'):
        self.fill = fill*block_size

    def write(self, addr, data):
        raise NotImplementedError
