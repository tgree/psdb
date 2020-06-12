# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from builtins import range

from psdb.devices import Device, Reg32
from .. import flash


# Conservative flash read wait states that work for all frequencies.
NRM_FLWAIT = 1
ORM_FLWAIT = 3


def to_hex(s):
    return ' '.join('%02X' % ord(c) for c in s)


def not_bytes(s):
    return ''.join(chr(0xFF & ~ord(c)) for c in s)


def or_bytes(l, r):
    return ''.join(chr(ord(lc) | ord(rc)) for lc, rc in zip(l, r))


def and_bytes(l, r):
    return ''.join(chr(ord(lc) & ord(rc)) for lc, rc in zip(l, r))


class UnlockedContextManager(object):
    def __init__(self, flash, mask):
        assert (mask & 0xFFFFFFFFFFFFFFFF) == mask
        self.flash = flash
        self.mask  = mask

    def __enter__(self):
        mask = [0xFFFFFFFF & ~(self.mask >>  0),
                0xFFFFFFFF & ~(self.mask >> 32)]
        self.flash._BANK0_MAIN_WEPROT = mask[0]
        self.flash._BANK1_MAIN_WEPROT = mask[1]

    def __exit__(self, type, value, traceback):
        self.flash._BANK0_MAIN_WEPROT = 0xFFFFFFFF
        self.flash._BANK1_MAIN_WEPROT = 0xFFFFFFFF


class FLCTL(Device, flash.Flash):
    '''
    Driver for the FLCTL device on the MSP432P401 series of MCUs.
    '''
    REGS = [Reg32('BANK0_RDCTL',       0x10),
            Reg32('BANK1_RDCTL',       0x14),
            Reg32('RDBRST_CTLSTAT',    0x20,   [('START',           1),
                                                ('MEM_TYPE',        2),
                                                ('STOP_FAIL',       1),
                                                ('DATA_CMP',        1),
                                                ('',                11),
                                                ('BRST_STAT',       2),
                                                ('CMP_ERR',         1),
                                                ('ADDR_ERR',        1),
                                                ('',                3),
                                                ('CLR_STAT',        1),
                                                ]),
            Reg32('RDBRST_STARTADDR',  0x24),
            Reg32('RDBRST_LEN',        0x28),
            Reg32('PRG_CTLSTAT',       0x50,   [('ENABLE',          1),
                                                ('MODE',            1),
                                                ('VER_PRE',         1),
                                                ('VER_PST',         1),
                                                ('',                12),
                                                ('STATUS',          2),
                                                ('BNK_ACT',         1),
                                                ]),
            Reg32('PRGBRST_CTLSTAT',   0x54,   [('START',           1),
                                                ('TYPE',            2),
                                                ('LEN',             3),
                                                ('AUTO_PRE',        1),
                                                ('AUTO_PST',        1),
                                                ('',                8),
                                                ('BURST_STATUS',    3),
                                                ('PRE_ERR',         1),
                                                ('PST_ERR',         1),
                                                ('ADDR_ERR',        1),
                                                ('',                1),
                                                ('CLR_STAT',        1),
                                                ]),
            Reg32('PRGBRST_STARTADDR', 0x58),
            Reg32('PRGBRST_DATA0_0',   0x60),
            Reg32('PRGBRST_DATA0_1',   0x64),
            Reg32('PRGBRST_DATA0_2',   0x68),
            Reg32('PRGBRST_DATA0_3',   0x6C),
            Reg32('PRGBRST_DATA1_0',   0x70),
            Reg32('PRGBRST_DATA1_1',   0x74),
            Reg32('PRGBRST_DATA1_2',   0x78),
            Reg32('PRGBRST_DATA1_3',   0x7C),
            Reg32('PRGBRST_DATA2_0',   0x80),
            Reg32('PRGBRST_DATA2_1',   0x84),
            Reg32('PRGBRST_DATA2_2',   0x88),
            Reg32('PRGBRST_DATA2_3',   0x8C),
            Reg32('PRGBRST_DATA3_0',   0x90),
            Reg32('PRGBRST_DATA3_1',   0x94),
            Reg32('PRGBRST_DATA3_2',   0x98),
            Reg32('PRGBRST_DATA3_3',   0x9C),
            Reg32('ERASE_CTLSTAT',     0xA0,   [('START',           1),
                                                ('MODE',            1),
                                                ('TYPE',            1),
                                                ('',                13),
                                                ('STATUS',          2),
                                                ('ADDR_ERR',        1),
                                                ('CLR_STAT',        1),
                                                ]),
            Reg32('ERASE_SECTADDR',    0xA4),
            Reg32('BANK0_MAIN_WEPROT', 0xB4),
            Reg32('BANK1_MAIN_WEPROT', 0xC4),
            Reg32('IFG',               0xF0),
            Reg32('CLRIFG',            0xF8),
            ]

    def __init__(self, target, ap, name, addr, flash_tlv_addr, **kwargs):
        Device.__init__(self, target, ap, addr, name, FLCTL.REGS, **kwargs)
        flash.Flash.__init__(self, 0x00000000, 4096, 64)
        self.target    = target
        self.flash_tlv = [self.ap.read_32(flash_tlv_addr + i*4)
                          for i in range(4)]
        assert self.flash_tlv[0] == 4
        assert self.flash_tlv[1] == 2

        self.max_programming_pulses = self.flash_tlv[2]
        self.max_erase_pulses       = self.flash_tlv[3]

    def _read_rdctl(self, addr):
        bank = addr // 0x00020000
        if bank == 0:
            return self._BANK0_RDCTL.read()
        elif bank == 1:
            return self._BANK1_RDCTL.read()
        else:
            raise Exception('Address 0x%08X not in flash!' % addr)

    def _write_rdctl(self, v, addr):
        bank = addr // 0x00020000
        if bank == 0:
            self._BANK0_RDCTL = v
        elif bank == 1:
            self._BANK1_RDCTL = v
        else:
            raise Exception('Address 0x%08X not in flash!' % addr)

    def _flash_mask_unlocked(self, mask):
        return UnlockedContextManager(self, mask)

    def _flash_addr_unlocked(self, addr):
        return self._flash_mask_unlocked(1 << (addr // 4096))

    def _set_rdmode(self, addr, mode):
        wait_states = NRM_FLWAIT if mode == 0 else ORM_FLWAIT
        self._write_rdctl((wait_states << 12) | mode, addr)
        while ((self._read_rdctl(addr) >> 16) & 0xF) != mode:
            pass

    def _set_rdbrst_idle(self):
        while self._RDBRST_CTLSTAT.BRST_STAT:
            self._RDBRST_CTLSTAT = (1 << 23)

    def _wait_rdbrst_complete(self):
        while True:
            ctlstat = self._RDBRST_CTLSTAT.read()
            if (ctlstat & 0x00030000) != 0x00030000:
                continue

            self._RDBRST_CTLSTAT = (1 << 23)
            return ctlstat

    def _set_erase_idle(self):
        while self._ERASE_CTLSTAT.STATUS:
            self._ERASE_CTLSTAT = (1 << 19)

    def _wait_erase_complete(self):
        while True:
            ctlstat = self._ERASE_CTLSTAT.read()
            if (ctlstat & 0x00030000) != 0x00030000:
                continue

            self._ERASE_CTLSTAT = (1 << 19)
            return ctlstat

    def _set_prgbrst_idle(self):
        while self._PRGBRST_CTLSTAT.BURST_STATUS:
            self._PRGBRST_CTLSTAT = (1 << 23)

    def _wait_prgbrst_complete(self):
        while True:
            ctlstat = self._PRGBRST_CTLSTAT.read()
            if (ctlstat & 0x00070000) != 0x00070000:
                continue

            self._PRGBRST_CTLSTAT = (1 << 23)
            return ctlstat

    def _write_burst_unlocked(self, addr, data_bytes):
        '''
        Bursts a 64-byte line into flash.  The flash must already have been
        erased and PRGBRST must already be idle.
        '''
        assert (addr & 0x3F) == 0
        assert len(data_bytes) == 64
        if data_bytes == '\xFF'*64:
            return

        verify_bits = (1 << 7) | (1 << 6)
        for _ in range(self.max_programming_pulses):
            self.ap.write_bulk(data_bytes, self.dev_base + 0x60)
            self._PRGBRST_STARTADDR = addr
            self._PRGBRST_CTLSTAT   = (verify_bits | (4 << 3) | 1)
            ctlstat = self._wait_prgbrst_complete()
            assert not (ctlstat & (1 << 21))

            if (ctlstat & ((1 << 19) | (1 << 20))) == 0:
                return

            if ctlstat & (1 << 19):
                # Pre-program auto-verify error.
                self._set_rdmode(addr, 3)
                exist_data       = self.ap.read_bulk(addr, 64)
                new_data         = data_bytes[:]
                fail_bits        = not_bytes(or_bytes(exist_data, new_data))
                updated_new_data = or_bytes(new_data, fail_bits)
                self._set_rdmode(addr, 0)
                if updated_new_data != '\xFF'*64:
                    print('0x%08X: Pre-program auto-verify error.' % addr)
                    print('      data_bytes: %s' % to_hex(data_bytes))
                    print('      exist_data: %s' % to_hex(exist_data))
                    print('       fail_bits: %s' % to_hex(fail_bits))
                    print('updated_new_data: %s' % to_hex(updated_new_data))
                    data_bytes   = updated_new_data
                    verify_bits &= ~(1 << 6)
                    continue

            if ctlstat & (1 << 20):
                # Post-program auto-verify error.
                self._set_rdmode(addr, 3)
                actual_data      = self.ap.read_bulk(addr, 64)
                temp_var         = data_bytes[:]
                fail_bits        = and_bytes(not_bytes(temp_var), actual_data)
                updated_new_data = not_bytes(fail_bits)
                self._set_rdmode(addr, 0)
                if fail_bits == '\x00'*64:
                    return
                print('0x%08X: Post-program auto-verify error.' % addr)
                print('      data_bytes: %s' % to_hex(data_bytes))
                print('     actual_data: %s' % to_hex(actual_data))
                print('       fail_bits: %s' % to_hex(fail_bits))
                print('updated_new_data: %s' % to_hex(updated_new_data))
                data_bytes   = updated_new_data
                verify_bits |= (1 << 6)

        raise flash.FlashWriteException(
                'Flash burst program failed for address 0x%08X!' % addr)

    def _write_burst(self, addr, data):
        '''
        Writes a 64-byte line of data using the burst program feature of the
        flash controller.  The address must be 64-byte aligned and the data to
        write must be exactly 64 bytes in length.

        The target line to be written must be in the erased state.
        '''
        assert self.target.is_halted()

        with self._flash_addr_unlocked(addr):
            self._set_prgbrst_idle()
            self._write_burst_unlocked(addr, data)

    def _write_sector(self, addr, data, verbose=True, already_erased=False):
        '''
        Writes a full 4096-byte sector to flash.  The sector will be
        automatically erased first if necessary.  The addr must be a multiple
        of 4096 and data must be a multiple of 64-bytes in length.
        '''
        assert self.target.is_halted()
        assert (len(data) % 64) == 0
        assert (addr & 0xFFF) == 0

        if verbose:
            print('Flashing sector 0x%08X...' % addr)

        if not already_erased:
            self.erase_sector(addr // self.sector_size, verbose=False)

        with self._flash_addr_unlocked(addr):
            self._set_prgbrst_idle()
            for i in range(0, len(data), 64):
                self._write_burst_unlocked(addr + i, data[i:i+64])

    def _write_bulk(self, addr, data, verbose=True):
        '''
        Writes 16-byte lines of data to the flash.  The address must be 16-byte
        aligned and the data to write must be a multiple of 16 bytes in length
        and should all be contained within one flash bank but may span multiple
        sectors.

        The target region to be written must be in the erased state.

        This is ridiculously faster compared to doing PRGBRST operations
        because we don't need to do a bunch of register setups.
        '''
        assert self.target.is_halted()
        if not data:
            return
        assert len(data) % 16 == 0
        assert addr % 16 == 0
        assert (addr & 0xFFFE0000) == ((addr + len(data) - 1) & 0xFFFE0000)

        if verbose:
            print('Flashing region [0x%08X - 0x%08X]...' % (
                    addr, addr + len(data) - 1))

        with self._flash_mask_unlocked(self._mask_for_alp(addr, len(data))):
            self._CLRIFG      = 0x0000033F
            self._PRG_CTLSTAT = 0x0000000B
            self.ap.write_bulk(data, addr)
            while self._PRG_CTLSTAT.STATUS:
                pass

            v = self._IFG.read()
            if v & 0x00000206:
                # TODO: If we see post-program verify errors, we need to switch
                #       to Program-Verify mode, re-read everything and find the
                #       lines that failed to program properly and pulse them
                #       again.
                #       Currently, we let the caller handle this by catching
                #       the exception and then reattempting using write_sector
                #       which is slower but handles multiple write pulses.
                raise flash.FlashWriteException(
                        'Flash operation failed, IFG=0x%08X' % v)

    def _verify_flash_erased(self, addr, length):
        '''
        Uses the read-burst feature of the flash controller to verify that the
        given data is erased with sufficient margining.  The address and length
        must both be multiples of the 16-byte read-burst line size.  The region
        must not cross a bank boundary.
        '''
        assert self.target.is_halted()
        assert (addr & 0xF) == 0
        assert (length & 0xF) == 0
        assert ((addr + length - 1) & ~0x1FFFF) == (addr & ~0x1FFFF)

        self._set_rdbrst_idle()
        self._set_rdmode(addr, 4)
        self._RDBRST_CTLSTAT   = ((1 << 4) | (1 << 3))
        self._RDBRST_STARTADDR = addr
        self._RDBRST_LEN       = length
        self._RDBRST_CTLSTAT   = ((1 << 4) | (1 << 3) | (1 << 0))
        ctlstat = self._wait_rdbrst_complete()
        self._set_rdmode(addr, 0)
        assert (ctlstat & (1 << 19)) == 0

        return (ctlstat & (1 << 18)) == 0

    def _verify_sector_erased(self, addr):
        '''
        Uses the read-burst feature of the flash controller to verify that the
        given sectors are erased with sufficient margining.  The address must
        be a multiple of the 4096-byte sector size.
        '''
        assert (addr & 0xFFF) == 0
        return self._verify_flash_erased(addr, 4096)

    def erase_sectors(self, mask, verbose=True):
        '''
        Erases the sectors in flash specified by the mask parameter using a
        mass-erase operation.  This erases all the sectors at once; the mask is
        64-bits wide and each set bit specifies whether or not to erase the
        corresponding sector, with the LSb mapping to sector 0 and the MSb
        mapping to sector 63.
        '''
        assert self.target.is_halted()
        assert (mask & 0xFFFFFFFFFFFFFFFF) == mask
        if verbose:
            print('Erasing mask 0x%016X...' % mask)

        for pulse in range(self.max_erase_pulses):
            with self._flash_mask_unlocked(mask):
                self._set_erase_idle()
                self._ERASE_CTLSTAT = ((1 << 1) | (1 << 0))
                ctlstat = self._wait_erase_complete()
                assert not (ctlstat & (1 << 18))

            for i in range(64):
                if (mask & (1 << i)) and self._verify_sector_erased(4096*i):
                    mask &= ~(1 << i)

            if mask == 0:
                return

            if pulse > 0:
                print('Re-erasing 0x%016X...' % mask)

        raise flash.FlashEraseException(
                'Failed to erase sectors mask 0x%016X' % mask)

    def erase_sector(self, n, verbose=True):
        '''
        Erases the nth sector in flash.
        The sector is verified to be erased before returning.
        '''
        assert 0 <= n and n < self.nsectors
        self.erase_sectors(1 << n, verbose)

    def read(self, addr, length):
        '''
        Reads a region from the flash.
        '''
        return self.ap.read_bulk(addr, length)

    def write(self, addr, data, verbose=True):
        '''
        Writes data to flash.  The data must be 16-byte aligned and be a
        multiple of 16 bytes in length.  The data must not span multiple flash
        banks.

        The target region should already have been erased.
        '''
        assert self.mem_base <= addr
        assert addr + len(data) <= self.mem_base + self.flash_size

        try:
            self._write_bulk(addr, data, verbose=verbose)
        except flash.FlashWriteException as e:
            # Hack until we implement proper pulsing in _write_bulk.
            if (addr & self.sector_mask) != 0:
                raise Exception('not aligned')
            if len(data) % 64:
                raise Exception('not 64-byte multiple')

            print('Exception doing bulk write; attempting burst writes')
            print('-- Exception: %s' % e)
            self._write_sector(addr, data, verbose=verbose,
                               already_erased=False)
