# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from ..block import RAMBD, BlockOutOfRangeException
import psdb

import math
import time
from builtins import range


class FlashException(Exception):
    pass


class FlashEraseException(Exception):
    pass


class FlashWriteException(Exception):
    pass


class Flash(object):
    def __init__(self, mem_base, sector_size, nsectors):
        super(Flash, self).__init__()
        self.mem_base    = mem_base
        self.sector_size = sector_size
        self.sector_mask = sector_size - 1
        self.flash_size  = sector_size * nsectors
        self.nsectors    = nsectors

    def _mask_for_alp(self, addr, length):
        '''
        Returns a bitmask of all sectors containing any part of the specified
        address-length pair.
        '''
        begin    = addr & ~self.sector_mask
        end      = addr + length + (-(addr + length) & self.sector_mask)
        nsectors = (end - begin) // self.sector_size
        fbit     = (begin - self.mem_base) // self.sector_size
        assert 0 <= fbit and fbit < self.nsectors
        assert 0 <= nsectors and fbit + nsectors <= self.nsectors
        return ((1 << nsectors) - 1) << fbit

    def _swap_addr(self, addr, data):
        '''
        Inverts the address about the midpoint of the flash.
        '''
        if addr < self.mem_base or addr > self.mem_base + self.flash_size:
            return addr

        halfsize = self.flash_size // 2
        midpoint = self.mem_base + halfsize
        assert (addr < midpoint) == (addr + len(data) <= midpoint)
        return (addr + halfsize) if addr < midpoint else (addr - halfsize)

    def set_swd_freq_write(self, verbose=True):
        '''
        Sets the probe's SWD clock frequency to one supported by the target for
        writing to flash.

        Only needs to be implemented if the max read/write frequencies differ.
        '''
        pass

    def set_swd_freq_read(self, verbose=True):
        '''
        Sets the probe's SWD clock frequency to one supported by the target for
        reading from flash.  This is typically the maximum SWD frequency
        supported by the target.

        Only needs to be implemented if the max read/write frequencies differ.
        '''
        pass

    def erase_sector(self, n, verbose=True):
        '''
        Erases the nth sector.
        '''
        raise NotImplementedError

    def erase_sectors(self, mask, verbose=True):
        '''
        Erases the sectors specified in the bit mask.
        '''
        sectors = []
        for i in range(int(math.floor(math.log(mask, 2))) + 1):
            if (mask & (1 << i)):
                sectors.append(i)
        for i in psdb.piter(sectors, verbose=verbose):
            self.erase_sector(i, verbose=False)

    def erase(self, addr, length, verbose=True):
        '''
        Erases the ALP from the flash.  If the ALP is not perfectly aligned
        to start and end sector boundaries, then the erase operation will also
        erase the edge sectors.
        '''
        self.erase_sectors(self._mask_for_alp(addr, length), verbose=verbose)

    def erase_all(self, verbose=True):
        '''
        Erases the entire flash.
        '''
        self.erase(self.mem_base, self.flash_size, verbose=verbose)

    def read(self, addr, length):
        '''
        Reads a region from the flash.
        '''
        raise NotImplementedError

    def read_all(self):
        '''
        Reads the entire flash.
        '''
        return self.read(self.mem_base, self.flash_size)

    def write(self, addr, data, verbose=True):
        '''
        Writes the specified bytes to the specified address in flash.  The
        region to be written must already be in the erased state.
        '''
        raise NotImplementedError

    def burn_dv(self, dv, bank_swap=False, verbose=True, erase=True):
        '''
        Burns the specified data vector to flash, erasing sectors as necessary
        to perform the operation.  The data vector is a list of the form:

            [(address, b'...'),
             (address, b'...'),
             ]

        Data is first prepared in a buffer; earlier vector elements will be
        overwritten by later elements if their ranges overlap.  Flash sectors
        untouched by the data vector are preserved; data between elements
        within a sector is erased.

        Data written to sectors outside flash boundaries is silently discarded.

        The bank_swap option can be used to invert data vector addresses about
        the midpoint of the flash.  So, for an 8K flash writes to the lower 4K
        would instead be performed to the upper 4K and writes to the upper 4K
        would be performed to the lower 4K.  This is to allow writing a binary
        linked at an active base address into the inactive half of flash in a
        dual-banked system.
        '''
        bd = RAMBD(self.sector_size,
                   first_block=self.mem_base // self.sector_size,
                   nblocks=self.nsectors)
        for v in dv:
            try:
                addr = self._swap_addr(v[0], v[1]) if bank_swap else v[0]
                bd.write(addr, v[1])
            except BlockOutOfRangeException:
                pass

        if erase:
            if verbose:
                print('Erasing flash...')
            mask = 0
            for block in bd.blocks.values():
                mask |= self._mask_for_alp(block.addr, len(block.data))
            self.erase_sectors(mask, verbose=verbose)

        self.set_swd_freq_write(verbose=verbose)

        t0 = time.time()
        total_len = 0
        if verbose:
            print('Burning flash...')
        for block in psdb.piter(bd.blocks.values(), verbose=verbose):
            while block.data.endswith(b'\xff'*64):
                block.data = block.data[:-64]
            self.write(block.addr, block.data, verbose=False)
            total_len += len(block.data)

        if verbose:
            elapsed = time.time() - t0
            print('Wrote %u bytes in %.2f seconds (%.2f K/s).' %
                  (total_len, elapsed, total_len / (1024*elapsed)))

        self.set_swd_freq_read(verbose=verbose)

        if verbose:
            print('Verifying flash...')
        t0 = time.time()
        for block in psdb.piter(bd.blocks.values(), verbose=verbose):
            mem = self.read(block.addr, len(block.data))
            assert mem == block.data
        if verbose:
            elapsed = time.time() - t0
            print('Verified %u bytes in %.2f seconds (%.2f K/s).' %
                  (total_len, elapsed, total_len / (1024*elapsed)))
