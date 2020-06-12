# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import sys
import math


FRAC_LUT = [
    u'\u2500',
    u'\u258F',
    u'\u258E',
    u'\u258D',
    u'\u258C',
    u'\u258B',
    u'\u258A',
    u'\u2589',
    ]


class piter(object):
    '''
    Iterator class that also displays a progress bar.
    '''
    def __init__(self, seq, width=40, verbose=True):
        self.seq     = seq
        self.width   = width
        self.verbose = verbose
        self.end     = len(seq)
        self._iter   = iter(seq)
        self.v       = 0

    def __repr__(self):
        frac, n_star = math.modf(self.v * self.width / self.end)
        frac         = int(frac * 8)
        n_star       = int(n_star)
        n_space      = self.width - n_star - 1

        s = u'\r\u2503' + u'\u2588'*n_star
        if n_space >= 0:
            s += FRAC_LUT[frac] + u'\u2500'*n_space
        s += (u'\u2503 [%u / %u]' % (self.v, self.end))

        return s

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.verbose:
            sys.stdout.write(repr(self))

        try:
            self.v += 1
            return next(self._iter)
        except StopIteration:
            if self.verbose:
                print()
            raise


def prange(*args):
    return piter(range(*args))
