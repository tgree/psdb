# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
from . import xds110
import psdb


__all__ = ['xds110',
           ]


def find(**kwargs):
    return psdb.probes.find(cls=xds110.XDS110, **kwargs)


def make_one(**kwargs):
    return psdb.probes.make_one(cls=xds110.XDS110, **kwargs)


def make_one_ns(ns):
    return psdb.probes.make_one_ns(ns, cls=xds110.XDS110)
