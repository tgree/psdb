#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import socket
import argparse
import threading
import time
from builtins import range, bytes

import psdb.probes

REG_MAP = [
    'r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11',
    'r12', 'sp', 'lr', 'pc', 'xpsr',
    ]

REG_REV_MAP = {
    0x00 : 'r0',
    0x01 : 'r1',
    0x02 : 'r2',
    0x03 : 'r3',
    0x04 : 'r4',
    0x05 : 'r5',
    0x06 : 'r6',
    0x07 : 'r7',
    0x08 : 'r8',
    0x09 : 'r9',
    0x0A : 'r10',
    0x0B : 'r11',
    0x0C : 'r12',
    0x0D : 'sp',
    0x0E : 'lr',
    0x0F : 'pc',
    0x19 : 'xpsr',
    }


class ConnectionClosedException(Exception):
    def __init__(self):
        super(ConnectionClosedException, self).__init__('Connection closed')


class GDBConnection(object):
    WAIT_DOLLAR = 1
    WAIT_SHARP  = 2
    WAIT_CHECK0 = 3
    WAIT_CHECK1 = 4

    def __init__(self, server, sock, verbose):
        self.server  = server
        self.sock    = sock
        self.verbose = verbose
        self.data    = b''

    def sendall(self, data):
        if self.verbose:
            print("Sending: '%s'" % data)
        self.sock.sendall(data)

    def recv(self, n, timeout=None):
        self.sock.settimeout(timeout)

        try:
            data = self.sock.recv(n)
        except socket.timeout:
            return None
        finally:
            self.sock.settimeout(None)

        if self.verbose:
            print("Received: '%s'" % data)
        return data

    def send_ack(self):
        self.sendall(b'+')

    def send_nack(self):
        self.sendall(b'-')

    def send_packet(self, data):
        csum   = (sum(ord(bytes([c])) for c in data) & 0xFF)
        packet = b'$%s#%02x' % (data, csum)
        self.sendall(packet)
        while True:
            char = self.recv(1)
            if not char:
                raise ConnectionClosedException()
            if char == b'-':
                self.sendall(packet)
            elif char == b'+':
                return

    def recv_packet(self):
        pkt   = b''
        state = GDBConnection.WAIT_DOLLAR
        while True:
            if not self.data:
                self.data = self.recv(1024)
                if not self.data:
                    raise ConnectionClosedException()

            if state == GDBConnection.WAIT_DOLLAR:
                if self.data[0:1] == b'\x03':
                    self.data = self.data[1:]
                    return b'\x03'
                front, delim, self.data = self.data.partition(b'$')
                if delim:
                    state = GDBConnection.WAIT_SHARP
            elif state == GDBConnection.WAIT_SHARP:
                front, delim, self.data = self.data.partition(b'#')
                pkt += front
                if delim:
                    state = GDBConnection.WAIT_CHECK0
            elif state == GDBConnection.WAIT_CHECK0:
                checksum   = (int(self.data[0:1], 16) << 4)
                self.data  = self.data[1:]
                state = GDBConnection.WAIT_CHECK1
            elif state == GDBConnection.WAIT_CHECK1:
                checksum  |= (int(self.data[0:1], 16) << 0)
                self.data  = self.data[1:]
                state = GDBConnection.WAIT_DOLLAR

                while b'$' in pkt:
                    _, _, pkt = pkt.partition(b'$')

                csum = (sum(ord(bytes([c])) for c in pkt) & 0xFF)
                if csum == checksum:
                    self.send_ack()
                    return pkt
                else:
                    self.send_nack()
                    if self.verbose:
                        print("Discarding (expected %02X): '%s'" % (csum, pkt))
                    pkt = ''

    def poll_break(self, timeout):
        assert not self.data
        t0 = time.time()
        data = self.recv(1, timeout=timeout)
        if data is None:
            print('Receive timed out after %.3f seconds' % (time.time() - t0))
            return False
        elif data == b'':
            raise ConnectionClosedException()

        assert data == b'\x03'
        return True


class GDBServer(object):
    STATE_HALTED  = 1
    STATE_RUNNING = 2

    def __init__(self, target, port, verbose, halted):
        self.handlers = {
                b'g'    : self._handle_read_registers,
                b'?'    : self._handle_question,
                b'G'    : self._handle_write_registers,
                b'm'    : self._handle_read_memory,
                b'M'    : self._handle_write_memory,
                b'c'    : self._handle_continue,
                b's'    : self._handle_step_instruction,
                b'Z'    : self._handle_insert_breakpoint,
                b'z'    : self._handle_remove_breakpoint,
                }
        self.target        = target
        self.port          = port
        self.verbose       = verbose
        self.state         = self.STATE_HALTED if halted else self.STATE_RUNNING
        self.thread        = threading.Thread(target=self._workloop)
        self.thread.daemon = True
        self.thread.start()

    def _workloop(self):
        listener = socket.socket()
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(('', self.port))
        listener.listen(5)

        while True:
            sock, remote = listener.accept()
            print('Accepted connection from %s' % (remote,))
            try:
                self._process_connection(sock)
            except ConnectionClosedException:
                print('Connection closed.')
            except psdb.probes.xds110.XDS110CommandException as e:
                print('XDS110 Exception: %s' % e)
                sock.shutdown(socket.SHUT_RDWR)
            finally:
                sock.close()

    def _halt(self):
        assert self.state == self.STATE_RUNNING

        self.target.halt()
        print('CPU halted. PC: 0x%08X'
              % self.target.cpus[0].read_core_register('pc'))
        self.state = self.STATE_HALTED

    def _resume(self):
        assert self.state == self.STATE_HALTED

        print('CPU started.')
        self.target.resume()
        self.state = self.STATE_RUNNING

    def _single_step(self):
        assert self.state == self.STATE_HALTED

        print('CPU stepping one instruction.')
        self.target.cpus[0].single_step()
        print('CPU halted. PC: 0x%08X'
              % self.target.cpus[0].read_core_register('pc'))

    def _process_connection(self, sock):
        if self.state == self.STATE_RUNNING:
            self._halt()

        gc = GDBConnection(self, sock, self.verbose)
        while True:
            if self.state == self.STATE_HALTED:
                self._process_connection_halted(gc)
            elif self.state == self.STATE_RUNNING:
                self._process_connection_running(gc)
            else:
                raise Exception('Weird state %u' % self.state)

    def _process_connection_halted(self, gc):
        pkt = gc.recv_packet()
        rsp = self.handlers.get(pkt[0:1], self._handle_unimplemented)(pkt)
        if rsp is not None:
            gc.send_packet(rsp)

    def _process_connection_running(self, gc):
        if gc.poll_break(timeout=0.1):
            print('Received BREAK request from gdb.')
            self._halt()
        elif not self.target.cpus[0].is_halted():
            time.sleep(0.01)
            return
        else:
            print('CPU halted itself. PC: 0x%08X'
                  % self.target.cpus[0].read_core_register('pc'))
            self.state = self.STATE_HALTED

        gc.send_packet(b'S05')

    def _handle_unimplemented(self, pkt):
        return b''

    def _handle_question(self, pkt):
        '''
        Returns the reason we stopped; we return signal 5 (TRAP).
        '''
        return b'S05'

    def _handle_read_registers(self, pkt):
        '''
        Returns the concatenation of all registers defined in the REG_MAP list.
        '''
        data = b''
        regs = self.target.cpus[0].read_core_registers()
        for r in REG_MAP:
            v = regs[r]
            data += b'%02x%02x%02x%02x' % ((v >>  0) & 0xFF,
                                           (v >>  8) & 0xFF,
                                           (v >> 16) & 0xFF,
                                           (v >> 24) & 0xFF)
        return data

    def _handle_write_registers(self, pkt):
        return b''

    def _handle_read_memory(self, pkt):
        '''
        Reads a block of memory.
        '''
        args = pkt[1:].split(b',')
        addr = int(args[0], 16)
        n    = int(args[1], 16)

        print('Reading %u bytes from 0x%08X' % (n, addr))
        try:
            mem = self.target.cpus[0].read_bulk(addr, n)
            return b''.join(b'%02x' % ord(bytes([b])) for b in mem)
        except Exception as e:
            print('Read threw exception. %s' % e)
            return b''

    def _handle_write_memory(self, pkt):
        '''
        Writes a block of memory.
        '''
        args  = pkt[1:].split(b',')
        addr  = int(args[0], 16)
        args  = args[1].split(b':')
        size  = int(args[0], 16)
        chars = args[1]
        assert len(chars) == size*2
        data = b''
        for i in range(size):
            v = int(chars[2*i:2*i+2], 16)
            data += bytes([v])

        try:
            self.target.cpus[0].write_bulk(data, addr)
            return b'OK'
        except Exception:
            print('Write threw exception.')
        return b'E01'

    def _handle_continue(self, pkt):
        '''
        Resumes execution.  The response is sent when/if the target halts in
        the future - either because the user interrupted us via Ctrl-C or we
        hit a breakpoint.  In either case, an S05 (TRAP) response should be
        returned to gdb.
        '''
        self._resume()

    def _handle_step_instruction(self, pkt):
        '''
        Resumes execution for a single instruction.
        '''
        self._single_step()
        return b'S05'

    def _handle_insert_breakpoint(self, pkt):
        if pkt[1:3] == b'0,':
            return self._handle_insert_software_breakpoint(pkt)
        if pkt[1:3] == b'1,':
            return self._handle_insert_hardware_breakpoint(pkt)
        return b'E01'

    def _handle_insert_software_breakpoint(self, pkt):
        # TODO: We should check if this is a flash or RAM address and insert
        #       a breakpoint instruction in RAM if possible.
        print('Delegating insert SW breakpoint to HW.')
        return self._handle_insert_hardware_breakpoint(pkt)

    def _handle_insert_hardware_breakpoint(self, pkt):
        # TODO: Semicolon!
        args = pkt[1:].split(b',')
        addr = int(args[1], 16)
        kind = int(args[2], 16)
        print('Inserting HW breakpoint 0x%08X of kind 0x%X' % (addr, kind))
        for c in self.target.cpus:
            c.bpu.insert_breakpoint(addr)
        return b'OK'

    def _handle_remove_breakpoint(self, pkt):
        if pkt[1:3] == b'0,':
            return self._handle_remove_software_breakpoint(pkt)
        if pkt[1:3] == b'1,':
            return self._handle_remove_hardware_breakpoint(pkt)
        return b'E01'

    def _handle_remove_software_breakpoint(self, pkt):
        # TODO: We should check if this is a flash or RAM address and remove
        #       a breakpoint instruction from RAM if possible.
        print('Delegating remove SW breakpoint to HW.')
        return self._handle_remove_hardware_breakpoint(pkt)

    def _handle_remove_hardware_breakpoint(self, pkt):
        # TODO: Semicolon!
        args = pkt[1:].split(b',')
        addr = int(args[1], 16)
        kind = int(args[2], 16)
        print('Removing HW breakpoint 0x%08X of kind 0x%X' % (addr, kind))
        for c in self.target.cpus:
            c.bpu.remove_breakpoint(addr)
        return b'OK'


def main(rv):
    if rv.dump:
        for p in psdb.probes.PROBES:
            p.show_info()
        return

    probe = psdb.probes.find_default(usb_path=rv.usb_path)
    probe.set_tck_freq(rv.probe_freq)

    if rv.srst:
        probe.srst_target()

    print('Starting server on port %s for %s' % (rv.port, probe))
    target = probe.probe(verbose=rv.verbose,
                         connect_under_reset=rv.connect_under_reset)
    target.set_max_tck_freq()

    for i, c in enumerate(target.cpus):
        if c.bpu is not None:
            c.bpu.reset()
            print('CPU%u: %s' % (i, c.bpu))

    if not rv.halt:
        target.resume()
    else:
        print('CPU halted. PC: 0x%08X'
              % target.cpus[0].read_core_register('pc'))
    GDBServer(target, rv.port, rv.verbose, rv.halt)

    while True:
        time.sleep(1)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=3333)
    parser.add_argument('--usb-path')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--dump', action='store_true')
    parser.add_argument('--connect-under-reset', action='store_true')
    parser.add_argument('--srst', action='store_true')
    parser.add_argument('--halt', action='store_true')
    main(parser.parse_args())


if __name__ == '__main__':
    _main()
