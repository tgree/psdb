# Copyright (c) 2020 by Phase Advanced Sensor Systems, Inc.


class LinkRef(object):
    def __init__(self, ap, addr):
        self.ap   = ap
        self.addr = addr

    def _read_next(self):
        return self.ap.read_32(self.addr + 0)

    def _read_prev(self):
        return self.ap.read_32(self.addr + 4)

    def _write_next(self, v):
        self.ap.write_32(v, self.addr + 0)

    def _write_prev(self, v):
        self.ap.write_32(v, self.addr + 4)


class QueueRef(object):
    '''
    A QueueRef is a class that can manipulate a standard circular queue (queue
    with bidirectional links and sentinel node).  A QueueRef is typically used
    when the queue has already been initialized by someone else.
    '''
    def __init__(self, ap, addr):
        self.ap   = ap
        self.addr = addr

    def _read_head(self):
        return self.ap.read_32(self.addr + 0)

    def _read_tail(self):
        return self.ap.read_32(self.addr + 4)

    def _write_head(self, v):
        self.ap.write_32(v, self.addr + 0)

    def _write_tail(self, v):
        self.ap.write_32(v, self.addr + 4)

    def _get_head_elem(self):
        return LinkRef(self.ap, self._read_head())

    def _get_tail_elem(self):
        return LinkRef(self.ap, self._read_tail())

    def is_empty(self):
        '''
        Returns True if the queue is empty, False otherwise.
        '''
        return self._read_head() == self.addr

    def clear(self):
        '''
        Clears the queue by writing directly to the head and tail pointers.
        '''
        self._write_head(self.addr)
        self._write_tail(self.addr)

    def front(self):
        '''
        Returns a LinkRef object for the first element in the queue.  Returns
        None if the queue is empty.
        '''
        head_elem = self._get_head_elem()
        if head_elem.addr == self.addr:
            return None
        return head_elem

    def push(self, link_addr):
        '''
        Pushes the specified element link to the tail of the queue.
        '''
        link_elem = LinkRef(self.ap, link_addr)
        tail_elem = self._get_tail_elem()
        link_elem._write_next(self.addr)
        link_elem._write_prev(tail_elem.addr)
        tail_elem._write_next(link_elem.addr)
        self._write_tail(link_elem.addr)

    def pop(self):
        '''
        Pops the head element off the queue and returns the address of the head
        elem.  Returns None if the queue is empty.
        '''
        head_elem = self.front()
        if head_elem is None:
            return None

        head_next_elem = LinkRef(self.ap, head_elem._read_next())
        head_next_elem._write_prev(self.addr)
        self._write_head(head_elem._read_next())
        return head_elem.addr

    def dump(self):
        '''
        Dump the queue contents.
        '''
        print('0x%08X Sentinel N: 0x%08X P: 0x%08X'
              % (self.addr, self._read_head(), self._read_tail()))
        link = LinkRef(self.ap, self.addr)
        while True:
            next_link_addr = link._read_next()
            if next_link_addr == self.addr:
                break

            link = LinkRef(self.ap, next_link_addr)
            print('0x%08X     Link N: 0x%08X P: 0x%08X'
                  % (link.addr, link._read_next(), link._read_prev()))


class Queue(QueueRef):
    '''
    A Queue is a class that can manipulate a standard circular queue (queue
    with bidirectional links and sentinel node).  The Queue class works exactly
    the same as the QueueRef class with the exception that the Queue memory is
    initialized to an empty queue when the object is constructed.
    '''
    def __init__(self, ap, addr):
        super(Queue, self).__init__(ap, addr)
        self.clear()
