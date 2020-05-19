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


def hexify(data):
    return ' '.join('%02X' % v for v in data)


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
    is part of the packet payload).  The actual event payload starts after the
    SUBEVTCODE field and its length is PAYLEN.

    This type of event must be freed back to the firmware using the MM
    return_evt_queue.  This is done automatically by the system_channel code;
    the object is effectively a copy of the event.  The only exception is if
    we are in FUS mode - the only event we get is the "ready" event and FUS
    does not implement the MM interface for it.
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


def write_ble_command(ap, addr, opcode, payload, next_ptr=0, prev_ptr=0):
    '''
    Command data type for the BLE channel.  The command is typically written to
    the BLE Table BLE Command Buffer and is not linked on a list.

        +-------------------------------------------------------------------+
        |                             NEXT PTR                              |
        +-------------------------------------------------------------------+
        |                             PREV PTR                              |
        +----------------+---------------------------------+----------------+
        |  TYPE = 0x01   |            CMDCODE              |     PAYLEN     | 
        +----------------+---------------------------------+----------------+
        |   PAYLOAD...
        +-----------------
    '''
    data = struct.pack('<LLBHB',
                       next_ptr,
                       prev_ptr,
                       0x01,
                       opcode,
                       len(payload)) + payload
    ap.write_bulk(data, addr)


class BLECommandStatus(object):
    '''
    Asynchronous command status event on the BLE event channel.

        +-------------------------------------------------------------------+
        |                             NEXT PTR                              |
        +-------------------------------------------------------------------+
        |                             PREV PTR                              |
        +----------------+----------------+----------------+----------------+
        |  TYPE = 0x04   | EVTCODE = 0x0F |   PAYLEN = 4   |     STATUS     |
        +----------------+----------------+----------------+----------------+
        |    NUMCMD      |             CMDCODE             |
        +----------------+---------------------------------+

    The NUMCMD field, when printed by some ST dump code, is listed as "numhci".
    Elsewhere, it is noted that this field indicates the number of commands
    that the BLE is willing to accept at once; typically this value is 1.

    This type of event is a Command Response and as such it should not be freed
    back to the MM.
    '''
    def __init__(self, ap, addr, data):
        self.addr = addr

        (plen,
         self.status,
         self.numcmd,
         self.cmdcode) = struct.unpack_from('BBBH', data, 2)
        assert plen == 4

    def __repr__(self):
        return ('BLECommandStatus({status: 0x%02X, numcmd: 0x%02X, '
                'cmdcode: 0x%04X})' % (self.status, self.numcmd, self.cmdcode))


class BLECommandComplete(object):
    '''
    Asynchronous command complete event on the BLE event channel.

        +-------------------------------------------------------------------+
        |                             NEXT PTR                              |
        +-------------------------------------------------------------------+
        |                             PREV PTR                              |
        +----------------+----------------+----------------+----------------+
        |  TYPE = 0x04   | EVTCODE = 0x0E |    PAYLEN+3    |     NUMCMD     |
        +----------------+----------------+----------------+----------------+
        |             CMDCODE             |   PAYLOAD...
        +---------------------------------+-----------------

    The NUMCMD field, when printed by some ST dump code, is listed as "numhci".
    Elsewhere, it is noted that this field indicates the number of commands
    that the BLE is willing to accept at once; typically this value is 1.

    This type of event is a Command Response and as such it should not be freed
    back to the MM.  In fact, this packet occupies the BLE Command Buffer used
    to send a command, so it would really break things to try and MM-free it.
    '''
    def __init__(self, ap, addr, data):
        self.addr = addr

        (plen,
         self.numcmd,
         self.cmdcode) = struct.unpack_from('BBH', data, 2)
        assert plen >= 3
        self.payload = ap.read_bulk(addr + 14, plen - 3)

    def __repr__(self):
        return ('BLECommandComplete({numcmd: 0x%02X, cmdcode: 0x%04X, '
                'payload: [%s]})' % (self.numcmd, self.cmdcode,
                                     hexify(self.payload)))


class BLE_VS_Event(object):
    '''
    Some sort of asynch event which seems to have the same structure as a
    system channel event.

        +-------------------------------------------------------------------+
        |                             NEXT PTR                              |
        +-------------------------------------------------------------------+
        |                             PREV PTR                              |
        +----------------+----------------+----------------+----------------+
        |  TYPE = 0x04   | EVTCODE = 0xFF |    PAYLEN+2    |  SUBEVTCODE   ...
        +----------------+----------------+----------------+----------------+
       ... SUBEVTCODE    |   PAYLOAD...
        +----------------+-----------------

    Since this type of event is not a Command Response, it does need to be
    freed back to the MM.
    '''
    def __init__(self, ap, addr, data):
        self.addr = addr

        (plen,
         self.subevtcode) = struct.unpack_from('BH', data, 2)
        assert plen >= 2
        self.payload = ap.read_bulk(addr + 13, plen - 2)

    def __repr__(self):
        return ('BLE_VS_Event({subevtcode: 0x%04X, payload: %s})'
                % (self.subevtcode, self.payload))


def make_ble_event(ap, addr):
    data = ap.read_bulk(addr + 8, 8)
    assert data[0] == 0x04
    assert data[1] in (0x0E, 0x0F, 0xFF)

    if data[1] == 0x0E:
        return BLECommandComplete(ap, addr, data)
    elif data[1] == 0x0F:
        return BLECommandStatus(ap, addr, data)
    elif data[1] == 0xFF:
        return BLE_VS_Event(ap, addr, data)
