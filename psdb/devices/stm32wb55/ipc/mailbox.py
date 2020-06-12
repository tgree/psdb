# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
import struct

from .circular_queue import Queue
from . import packet


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

    def _serialize_base_table(self):
        return struct.pack('<LLLLLLLLL',
                           self.dit_addr,
                           self.blet_addr,
                           0x00000000,
                           self.st_addr,
                           self.mmt_addr,
                           0x00000000,
                           0x00000000,
                           0x00000000,
                           0x00000000)

    def _serialize_system_table(self):
        return struct.pack('<LL',
                           self.sys_cmd_buffer_addr,
                           self.sys_queue_addr)

    def _serialize_ble_table(self):
        return struct.pack('<LLLL',
                           self.ble_cmd_buffer_addr,
                           self.ble_csbuffer_addr,
                           self.ble_evt_queue_addr,
                           self.ble_hci_acl_data_buffer_addr)

    def _serialize_mm_table(self):
        return struct.pack('<LLLLLLL',
                           self.mm_ble_buffer_addr,
                           self.mm_sys_buffer_addr,
                           self.mm_ble_pool_addr,
                           self.mm_ble_pool_len,
                           self.mm_return_evt_queue_addr,
                           0x00000000,
                           0x00000000)

    def write_tables(self):
        r'''
        Writes functional mailbox tables to the IPCC mailbox base address.  The
        different types of firmware have different minimal table requirements:

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
        0x20030004  0x20030280  BLE Table base address
        0x20030008  0x00000000  NULL (Thread Table base address)
        0x2003000C  0x20030200  System Table base address
        0x20030010  0x20030300  Mem Manager Table base address
        0x20030014  0x00000000  NULL (Trace Table base address)
        0x20030018  0x00000000  NULL (MAC 802.15.4 Table base address)
        0x2003001C  0x00000000  NULL (Zigbee Table base address)
        0x20030020  0x00000000  NULL (LLD Tests Table base address)

        --------------- Device Info Table (256 bytes) -----------------------
        0x20030100  ..........  Filled out by firmware

        --------------- System Table (128 bytes) ----------------------------
        0x20030200  0x20030400  Command Buffer address
        0x20030204  0x20030240  System Queue address
        ---------------------------------------------------------------------
        0x20030240  0x20030240  System Queue head
        0x20030244  0x20030240  System Queue tail

        --------------- BLE Table (128 bytes) -------------------------------
        0x20030280  0x20030600  BLE Command Buffer address
        0x20030284  0x200302B0  CsBuffer: min 15 bytes
        0x20030288  0x200302A0  Event Queue address
        0x2003028C  0x20030800  HciAclDataBuffer: 264 bytes
        ---------------------------------------------------------------------
        0x200302A0  0x200302A0  Event Queue head
        0x200302A4  0x200302A0  Event Queue tail
        ---------------------------------------------------------------------
        0x200302B0  ..........  CsBuffer

        --------------- Memory Manager Table (256 bytes) --------------------
        0x20030300  0x20030A00  Spare BLE buffer address
        0x20030304  0x20030C00  Spare System event buffer address
        0x20030308  0x20030E00  BLE Pool
        0x2003030C  0x00000800  BLE Pool Size: 2048 bytes
        0x20030310  0x20030340  Event Free Buffer Queue address
        0x20030314  0x00000000  Trace Event Pool address
        0x20030318  0x00000000  Trace Poll Size: 0 bytes
        ---------------------------------------------------------------------
        0x20030340  0x20030340  Event Free Buffer Queue head
        0x20030344  0x20030340  Event Free Buffer Queue tail

        --------------- System Command Buffer (512 bytes) -------------------
        0x20030400  ..........  Command or response packet

        --------------- BLE Command Buffer (512 bytes) ----------------------
        0x20030600  ..........  Command or response packet

        --------------- BLE HCI ACL Data Buffer (512 bytes) -----------------
        0x20030800  ..........  Command or response packet

        --------------- MM Spare BLE Buffer (512 bytes) ---------------------
        0x20030A00  ..........  Something BLE

        --------------- MM Spare System Event Buffer (512 bytes) ------------
        0x20030C00  ..........  Buffer used by FUS firmware for events

        --------------- MM BLE Pool (2048 bytes) ----------------------------
        0x20030E00  ..........  Memory pool used by BLE
        '''
        self.dit_addr                     = self.base_addr + 0x100
        self.st_addr                      = self.base_addr + 0x200
        self.sys_queue_addr               = self.base_addr + 0x240
        self.blet_addr                    = self.base_addr + 0x280
        self.ble_evt_queue_addr           = self.base_addr + 0x2A0
        self.ble_csbuffer_addr            = self.base_addr + 0x2B0
        self.mmt_addr                     = self.base_addr + 0x300
        self.mm_return_evt_queue_addr     = self.base_addr + 0x340
        self.sys_cmd_buffer_addr          = self.base_addr + 0x400
        self.ble_cmd_buffer_addr          = self.base_addr + 0x600
        self.ble_hci_acl_data_buffer_addr = self.base_addr + 0x800
        self.mm_ble_buffer_addr           = self.base_addr + 0xA00
        self.mm_sys_buffer_addr           = self.base_addr + 0xC00
        self.mm_ble_pool_addr             = self.base_addr + 0xE00
        self.mm_ble_pool_len              = 2048
        assert self.ram_size >= 0xE00 + 2048

        self.ap.write_bulk(b'\xCC'*self.ram_size, self.base_addr)
        self.ap.write_bulk(self._serialize_base_table(), self.base_addr)
        self.ap.write_bulk(self._serialize_system_table(), self.st_addr)
        self.ap.write_bulk(self._serialize_ble_table(), self.blet_addr)
        self.ap.write_bulk(self._serialize_mm_table(), self.mmt_addr)

        self.sys_queue        = Queue(self.ap, self.sys_queue_addr)
        self.ble_evt_queue    = Queue(self.ap, self.ble_evt_queue_addr)
        self.return_evt_queue = Queue(self.ap, self.mm_return_evt_queue_addr)

    def check_dit_key_fus(self):
        '''
        Checks the first 4 bytes of the Device Info Table to see if they
        contain the FUS key.
        '''
        return self.ap.read_32(self.dit_addr) == 0xA94656B9

    def read_stack_info(self):
        '''
        Returns the stack info field when the WS firmware is running.
        '''
        return self.ap.read_32(self.dit_addr + 24)

    def read_stack_type(self):
        '''
        Returns the stack type field when the WS firmware is running.
        '''
        return (self.read_stack_info() & 0xFF)

    def write_sys_command(self, opcode, payload):
        '''
        Writes a command packet to the system command buffer address.
        '''
        packet.write_sys_command(self.ap, self.sys_cmd_buffer_addr, opcode,
                                 payload)

    def read_sys_response(self):
        '''
        Reads the response packet from the system command buffer address.  Note
        that system channel responses do not include the linked-list header in
        their response.
        '''
        return packet.SysResponse(self.ap, self.sys_cmd_buffer_addr)

    def pop_sys_event(self):
        '''
        Pops an event from the system event queue if one is available and
        returns it; returns None if no event is available.
        '''
        evt_addr = self.sys_queue.pop()
        if evt_addr is None:
            return None

        return packet.SysEvent(self.ap, evt_addr)

    def write_ble_command(self, cmdcode, payload):
        '''
        Writes a command packet to the BLE command buffer address.
        '''
        packet.write_ble_command(self.ap, self.ble_cmd_buffer_addr, cmdcode,
                                 payload)

    def pop_ble_event(self):
        '''
        Pops an event from the BLE event queue if one is available and returns
        it; returns None if no event is available.
        '''
        evt_addr = self.ble_evt_queue.pop()
        if evt_addr is None:
            return None

        return packet.make_ble_event(self.ap, evt_addr)
