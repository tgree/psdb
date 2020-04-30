# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import struct


class SysResponse(object):
    def __init__(self, num_hci, opcode, status, payload):
        self.num_hci = num_hci
        self.opcode  = opcode
        self.status  = status
        self.payload = payload

    def dump(self):
        print('Num HCI: %u' % self.num_hci)
        print(' Opcode: 0x%04X' % self.opcode)
        print(' Status: 0x%02X' % self.status)
        print('Payload: %s' % self.payload)

    def __repr__(self):
        return ('SysResponse({num_hci: %u, opcode: 0x%04X, status: 0x%02X, '
                'payload: %s})' % (self.num_hci, self.opcode, self.status,
                                   self.payload))


class SysEvent(object):
    def __init__(self, addr, subevtcode, payload):
        self.addr       = addr
        self.subevtcode = subevtcode
        self.payload    = payload

    def dump(self):
        print('   Address: 0x%08X' % self.addr)
        print('SubEvtCode: 0x%04X' % self.subevtcode)
        print('   Payload: %s' % self.payload)

    def __repr__(self):
        return ('SysEvent({subevtcode: 0x%04X, payload: %s})'
            % (self.subevtcode, self.payload))


class Mailbox(object):
    '''
    Mailbox class for managing data structures used for interfacing with CPU2
    firmware.  Located somwhere in SRAM2a, according to the IPCCDBA address.
    '''
    def __init__(self, ap, base_addr, ram_size):
        # Fun fact: depending on what CPU2 firmware is running, the amount of
        # available RAM and secure boundary in SRAM2a moves around.  When re-
        # probing a newly-reset target, we hold on to the old Mailbox object
        # (probably a bad idea).  We need to size our tables so that they fit
        # in the smallest-common-denominator.
        self.ap        = ap
        self.base_addr = base_addr
        self.ram_size  = ram_size

    def _queue_pop(self, addr):
        '''
        Pops the head element off the queue at the specified address, and
        returns the address of the head elem.  Returns None if the queue is
        empty.
        '''
        head, = struct.unpack('<L', self.ap.read_bulk(addr, 4))
        if head == addr:
            return None

        data = self.ap.read_bulk(head, 8)
        n, p = struct.unpack('<LL', data)
        self.ap.write_bulk(struct.pack('<L', addr), n + 4)
        self.ap.write_bulk(struct.pack('<L', n), addr)
        return head

    def _queue_push(self, queue_addr, link_addr):
        '''
        Pushes the specified element link to the tail of the specified queue.
        '''
        data       = self.ap.read_bulk(queue_addr, 8)
        head, tail = struct.unpack('<LL', data)
        self.ap.write_bulk(struct.pack('<L', queue_addr), link_addr + 0)
        self.ap.write_bulk(struct.pack('<L', tail),       link_addr + 4)
        self.ap.write_bulk(struct.pack('<L', link_addr),  tail + 0)
        self.ap.write_bulk(struct.pack('<L', link_addr),  queue_addr + 4)

    def _serialize_base_table(self):
        return struct.pack('<LLLLLLLLL',
                           self.dit_addr,
                           0x00000000,
                           0x00000000,
                           self.st_addr,
                           self.mmt_addr,
                           0x00000000,
                           0x00000000,
                           0x00000000,
                           0x00000000)

    def _serialize_system_table(self):
        return struct.pack('<LLL',
                           self.sys_cmd_buffer_addr,
                           self.st_addr + 4,
                           self.st_addr + 4)

    def _serialize_mm_table(self):
        return struct.pack('<LLLLLLL',
                           self.ble_buffer_addr,
                           self.sys_buffer_addr,
                           self.ble_pool_addr,
                           self.ble_pool_len,
                           self.return_evt_queue_addr,
                           0x00000000,
                           0x00000000)

    def _serialize_evt_queue(self):
        return struct.pack('<LL',
                           self.return_evt_queue_addr,
                           self.return_evt_queue_addr)

    def write_tables(self):
        '''
        Writes functional mailbox tables to the IPCC mailbox base address.  The
        different types of firmware have different table requirements:

            | Table        \ FW: | FUS | BLE |
            +---------------+----+-----+-----+
            | Device Info Table  |  *  |  *  |
            | BLE Table          |     |     |
            | Thread Table       |     |     |
            | System Table       |  *  |  *  |
            | Mem Manager Table  |     |  *  |
            | Trace Table        |     |     |
            | MAC 802.15.4 Table |     |     |
            | Zigbee Table       |     |     |
            | LLD Tests Table    |     |     |
            +--------------------+-----+-----+

        Note that if you are trying to get to FUS, the currently-executing CPU2
        firmware may have a larger table requirement and you must satisfy that
        requirement for that firmware to boot up far enough for you to then
        send the command to switch to FUS.

        The addresses of each table are flexible since the base table just
        contains pointers to all the other tables.  We selected a generously-
        spaced configuration for ease of viewing in a debugger.

        Address     Contents
        --------------- Base Table (256 byes) -------------------------------
        0x20030000  0x20030100  Device Info Table base address
        0x20030004  0x00000000  NULL (BLE Table base address)
        0x20030008  0x00000000  NULL (Thread Table base address)
        0x2003000C  0x20030200  System Table base address
        0x20030010  0x20030300  Mem Manager Table base address
        0x20030014  0x00000000  NULL (Trace Table base address)
        0x20030018  0x00000000  NULL (MAC 802.15.4 Table base address)
        0x2003001C  0x00000000  NULL (Zigbee Table base address)
        0x20030020  0x00000000  NULL (LLD Tests Table base address)

        --------------- Device Info Table (256 bytes) -----------------------
        0x20030100  ..........  Filled out by firmware

        --------------- System Table (256 bytes) ----------------------------
        0x20030200  0x20030400  Command Buffer address
        0x20030204  0x20030204  System Queue head
        0x20030208  0x20030204  System Queue tail

        --------------- Memory Manager Table (256 bytes) --------------------
        0x20030300  0x20030600  Spare BLE buffer address
        0x20030304  0x20030800  Spare System event buffer address
        0x20030308  0x20030A00  BLE Pool
        0x2003030C  0x00000800  BLE Pool Size: 2048 bytes
        0x20030310  0x20030340  Event Free Buffer Queue address
        0x20030314  0x00000000  Trace Event Pool address
        0x20030318  0x00000000  Trace Poll Size: 0 bytes
        0x20030340  0x20030340  Event Free Buffer Queue head
        0x20030340  0x20030340  Event Free Buffer Queue tail

        --------------- Command Buffer (512 bytes) --------------------------
        0x20030400  ..........  Command or response packet

        --------------- Spare BLE Buffer (512 bytes) ------------------------
        0x20030600  ..........  Something BLE

        --------------- Spare System Event Buffer (512 bytes) ---------------
        0x20030800  ..........  Buffer used by FUS firmware for events

        --------------- BLE Pool (2048 bytes) -------------------------------
        0x20030A00  ..........  Memory pool used by BLE
        '''
        self.dit_addr              = self.base_addr + 0x100
        self.st_addr               = self.base_addr + 0x200
        self.mmt_addr              = self.base_addr + 0x300
        self.return_evt_queue_addr = self.base_addr + 0x340
        self.sys_cmd_buffer_addr   = self.base_addr + 0x400
        self.ble_buffer_addr       = self.base_addr + 0x600
        self.sys_buffer_addr       = self.base_addr + 0x800
        self.ble_pool_addr         = self.base_addr + 0xA00
        self.ble_pool_len          = 2048
        assert self.ram_size >= 0xA00 + 2048

        self.ap.write_bulk(b'\xCC'*self.ram_size, self.base_addr)
        self.ap.write_bulk(self._serialize_base_table(), self.base_addr)
        self.ap.write_bulk(self._serialize_system_table(), self.st_addr)
        self.ap.write_bulk(self._serialize_mm_table(), self.mmt_addr)
        self.ap.write_bulk(self._serialize_evt_queue(),
                           self.return_evt_queue_addr)

    def check_dit_key_fus(self):
        '''
        Checks the first 4 bytes of the Device Info Table to see if they
        contain the FUS key.
        '''
        return self.ap.read_32(self.dit_addr) == 0xA94656B9

    def get_fus_version(self):
        '''
        Asserts that we are in FUS mode then returns the FUS version field.
        '''
        assert self.check_dit_key_fus()
        return self.ap.read_32(self.dit_addr + 12)

    def get_ws_version(self):
        '''
        Asserts that we are in FUS mode then returns the FUS version field.
        '''
        assert self.check_dit_key_fus()
        return self.ap.read_32(self.dit_addr + 20)

    def write_sys_command(self, opcode, payload):
        '''
        Writes a command packet to the system command buffer address.
        '''
        data = struct.pack('<LLBHB',
                           0x00000000,
                           0x00000000,
                           0x10,
                           opcode,
                           len(payload)) + payload
        self.ap.write_bulk(data, self.sys_cmd_buffer_addr)

    def read_sys_response(self):
        '''
        Reads the response packet from the system command buffer address.  Note
        that system channel responses do not include the linked-list header in
        their response.
        '''
        hdr = self.ap.read_bulk(self.sys_cmd_buffer_addr, 7)
        (_type, evtcode, plen, num_hci,
         opcode, status) = struct.unpack('<BBBBHB', hdr)
        assert _type   == 0x11
        assert evtcode == 0x0E
        assert plen    >= 4
        payload = self.ap.read_bulk(self.sys_cmd_buffer_addr + 7, plen - 4)
        return SysResponse(num_hci, opcode, status, payload)

    def pop_sys_event(self):
        '''
        Pops an event from the system event queue if one is available and
        returns it; returns None if no event is available.
        '''
        evt_addr = self._queue_pop(self.st_addr + 4)
        if evt_addr is None:
            return None

        data = self.ap.read_bulk(evt_addr + 8, 5)
        (_type,
         evtcode,
         plen,
         subevtcode) = struct.unpack('<BBBH', data)
        payload = self.ap.read_bulk(evt_addr + 13, plen - 2)
        return SysEvent(evt_addr, subevtcode, payload)

    def push_mm_free_event(self, evt):
        '''
        Pushes an event to the memory manager return event queue tail.  This
        queue is used to return events back to the firmware that it allocated
        out of its memory pool when posting an event.
        '''
        self._queue_push(self.return_evt_queue_addr, evt.addr)
