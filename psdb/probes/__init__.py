# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from . import xds110
from . import stlink
from . import xtswd
from .probe import Enumeration, Probe


PROBE_CLASSES = [
    stlink,
    xds110,
    xtswd,
]

PROBE_KEYS = [
    'serial_num',
    'usb_path',
    'max_tck_freq',
]


def find(cls=Probe, **kwargs):
    return Enumeration.filter(cls.find(), **kwargs)


def make_one(cls=Probe, **kwargs):
    return cls.make_one(**kwargs)


def make_one_ns(ns, cls=Probe):
    keys = {k : v for k, v in vars(ns).items()
            if k in PROBE_KEYS and v is not None}
    return make_one(cls=cls, **keys)


def dump_probes():
    for e in find():
        try:
            p = e.make_probe()
        except Exception as ex:
            e.show_info()
            print('Exception making probe: %s' % ex)
            continue

        p.show_detailed_info()
