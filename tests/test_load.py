#!/usr/bin/env python
"""
Test loading
"""

import os
schema_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"schemas")

import lcatr.schema

def test_do_explicit():
    for what in ["json","py"]:
        fname = os.path.join(schema_dir,"%sexample.schema"%what)
        lcatr.schema.load(fname)
        
def test_count():
    assert "average" in lcatr.schema.store.keys(), 'Schema "average" not found'
    navgs = len(lcatr.schema.store['average'])
    assert navgs == 2, 'Unexpected number of schemas for "average" %d != 2' % navgs


def test_env():
    os.environ['LCATR_SCHEMA_PATH'] = schema_dir
    lcatr.schema.load_all()

def test_get():
    sd = lcatr.schema.get("average")
    s0 = lcatr.schema.get("average",0)
    s1 = lcatr.schema.get("average",1)
    se = lcatr.schema.get("average",2)

    assert sd == s1, "Default schema isn't highest."
    assert se is None, "Got a schema where we should get none."
    return

def test_make():
    s = lcatr.schema.get("average")
    v = lcatr.schema.valid(s, count=3, sum=2, sum2=8)
    v = lcatr.schema.valid(s, count=3, sum=2, sum2=8, extra="okay")
    try:
        fail = lcatr.schema.valid(s, count=3, sum=2, sum2="eight")
    except ValueError,msg:
        if not "could not convert string to float: eight" in msg:
            raise
    else:
        raise

    try:
        fail = lcatr.schema.valid(s, count=3, sum=2)
    except ValueError,msg:
        if not 'Missing required keyword argument: "sum2"' in msg:
            raise
    else:
        raise

    try:
        fail = lcatr.schema.valid(s, count=3, sum=2, sum2=2, schema_version=42)
    except ValueError,msg:
        if not 'Schema mismatch: schema_version differs: 1 != 42' in msg:
            raise
    else:
        raise

if __name__ == '__main__':
    test_do_explicit()
    test_count()
    test_env()
    test_count()
    test_get()
    test_make()
