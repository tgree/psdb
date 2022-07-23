# Copyright (c) 2019 Phase Advanced Sensor Systems, Inc.
import psdb
from . import stlink_v2_1
from . import stlink_v3
from . import stlink
from .cdb import CMD_ADDRESS, CMD_WRITE, CMD_READ, CMD_APNUM


__all__ = ['CMD_ADDRESS',
           'CMD_APNUM',
           'CMD_READ',
           'CMD_WRITE',
           'stlink_v2_1',
           'stlink_v3',
           ]


def find(**kwargs):
    return (psdb.probes.find(cls=stlink_v2_1.STLinkV2_1, **kwargs) +
            psdb.probes.find(cls=stlink_v3.STLinkV3, **kwargs))


def make_one(**kwargs):
    return psdb.probes.make_one(cls=stlink.STLink, **kwargs)


def make_one_ns(ns):
    return psdb.probes.make_one_ns(ns, cls=stlink.STLink)
