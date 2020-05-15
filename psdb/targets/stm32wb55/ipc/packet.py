# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.
'''
Code for dealing with "packets" from the firmware.  Packets can be either
commands, responses or events.  The packets typically also include an 8-byte
doubly-linked-list link header consisting of next/prev pointers, but for the
case of a system command response packet these pointers are not present and the
event pointer is straight to the TL_EvtSerial_t payload.

In all cases, the maximum payload length is 255 bytes - the presence or absence
of the linked-list pointers doesn't limit the size of the rest of the packet.
'''
import struct


def write_sys_command(ap, addr, opcode, payload, next_ptr=0, prev_ptr=0):
    '''
    Command data type for the system channel.  The command is typically written
    to the system command buffer and is not linked on a list until it is
    returned to us later.

        +-------------------------------------------------------------------+
        |                             NEXT PTR                              |
        +-------------------------------------------------------------------+
        |                             PREV PTR                              |
        +----------------+---------------------------------+----------------+
        |  TYPE = 0x10   |             OPCODE              |     PAYLEN     | 
        +----------------+---------------------------------+----------------+
        |   PAYLOAD...
        +-----------------
    '''
    data = struct.pack('<LLBHB',
                       next_ptr,
                       prev_ptr,
                       0x10,
                       opcode,
                       len(payload)) + payload
    ap.write_bulk(data, addr)


class SysResponse(object):
    '''
    Response data type for the system channel.  Response packets on the system
    channel do NOT include the doubly-linked-list link header (next/prev
    pointers), unlike all other types of event packet.

        +----------------+----------------+----------------+----------------+
        |  TYPE = 0x11   | EVTCODE = 0x0E |    PAYLEN+4    | NUM_HCI = 0xFF |
        +----------------+----------------+----------------+----------------+
        |             OPCODE              |     STATUS     |   PAYLOAD...
        +---------------------------------+----------------+-----------------

    The packet payload starts immediately after the PAYLEN field (NUM_HCI,
    OPCODE and STATUS are all part of the packet payload).  The actual response
    payload starts after the STATUS field and its length is PAYLEN.
    '''
    def __init__(self, ap, addr):
        hdr = ap.read_bulk(addr, 7)
        (_type, evtcode, plen, self.num_hci,
         self.opcode, self.status) = struct.unpack('<BBBBHB', hdr)
        assert _type   == 0x11
        assert evtcode == 0x0E
        assert plen    >= 4
        self.payload = ap.read_bulk(addr + 7, plen - 4)

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
    '''
    Asynchronous event on the system channel.

        +-------------------------------------------------------------------+
        |                             NEXT PTR                              |
        +-------------------------------------------------------------------+
        |                             PREV PTR                              |
        +----------------+----------------+----------------+----------------+
        |  TYPE = 0x12   | EVTCODE = 0xFF |    PAYLEN+2    |  SUBEVTCODE   ...
        +----------------+----------------+----------------+----------------+
       ... SUBEVTCODE    |   PAYLOAD...
        +----------------+-----------------

    The packet payload starts immediately after the PAYLEN field (SUBEVTCODE
    is part of the packet payload).  The actuel event payload starts after the
    SUBEVTCODE field and its length is PAYLEN.
    '''
    def __init__(self, ap, addr):
        self.addr = addr

        data = ap.read_bulk(addr + 8, 5)
        (_type,
         evtcode,
         plen,
         self.subevtcode) = struct.unpack('<BBBH', data)
        assert _type   == 0x12
        assert evtcode == 0xFF
        assert plen    >= 2
        self.payload = ap.read_bulk(addr + 13, plen - 2)

    def dump(self):
        print('   Address: 0x%08X' % self.addr)
        print('SubEvtCode: 0x%04X' % self.subevtcode)
        print('   Payload: %s' % self.payload)

    def __repr__(self):
        return ('SysEvent({subevtcode: 0x%04X, payload: %s})'
            % (self.subevtcode, self.payload))


