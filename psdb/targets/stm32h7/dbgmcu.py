# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.


# Address of the DBGMCU when accessed via AP2.  When accessed via either of the
# CPU APs, it is at 0x5C001000.  We use AP2 so that we can access it even if
# one of the CPUs we would normally use is disabled.
DBGMCU_BASE = 0xE00E1000


def read_idc(db):
    return db.aps[2].read_32(DBGMCU_BASE + 0)


def read_idc_dev_id(db):
    return db.aps[2].read_32(DBGMCU_BASE + 0) & 0xFFF


def read_cr(db):
    return db.aps[2].read_32(DBGMCU_BASE + 4)


def write_cr(db, v):
    db.aps[2].write_32(v, DBGMCU_BASE + 4)
