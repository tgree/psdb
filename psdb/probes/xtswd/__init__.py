# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import psdb
from . import xtswd


__all__ = [
    'xtswd',
]


def find(**kwargs):
    return psdb.probes.find(cls=xtswd.XTSWD, **kwargs)


def make_one(**kwargs):
    return psdb.probes.make_one(cls=xtswd.XTSWD, **kwargs)


def make_one_ns(ns):
    return psdb.probes.make_one_ns(ns, cls=xtswd.XTSWD)
