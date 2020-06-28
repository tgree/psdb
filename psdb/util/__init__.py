# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
from .prange import piter, prange
from .hexify import hexify


def round_up_pow_2(v, p2):
    return ((v + p2 - 1) & ~(p2 - 1))


__all__ = ['hexify',
           'piter',
           'prange',
           'round_up_pow_2',
           ]
