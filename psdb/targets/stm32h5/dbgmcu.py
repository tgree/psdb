# Copyright (c) 2026 Phase Advanced Sensor Systems, Inc.


# Address of the DBGMCU when accessed via AP0.
DBGMCU_BASE = 0xE00E4000


def read_idc(db):
    return db.aps[0].read_32(DBGMCU_BASE + 0)


def read_idc_dev_id(db):
    return db.aps[0].read_32(DBGMCU_BASE + 0) & 0xFFF


def read_cr(db):
    return db.aps[0].read_32(DBGMCU_BASE + 4)


def write_cr(db, v):
    db.aps[0].write_32(v, DBGMCU_BASE + 4)
