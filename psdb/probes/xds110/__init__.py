# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb
from .xds110 import XDS110, XDS110CommandException


__all__ = ['XDS110CommandException',
           ]


def find(**kwargs):
    return psdb.probes.find(cls=XDS110, **kwargs)


def make_one(**kwargs):
    return psdb.probes.make_one(cls=XDS110, **kwargs)


def make_one_ns(ns):
    return psdb.probes.make_one_ns(ns, cls=XDS110)
