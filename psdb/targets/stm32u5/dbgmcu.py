# Copyright (c) 2020-2021 Phase Advanced Sensor Systems, Inc.


DBGMCU_BASE = 0xE0044000


def read_idc(db):
    return db.aps[0].read_32(DBGMCU_BASE + 0)


def read_idc_dev_id(db):
    return db.aps[0].read_32(DBGMCU_BASE + 0) & 0xFFF


def read_cr(db):
    return db.aps[0].read_32(DBGMCU_BASE + 4)


def write_cr(db, v):
    db.aps[0].write_32(v, DBGMCU_BASE + 4)
