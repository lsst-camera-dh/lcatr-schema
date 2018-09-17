#!/usr/bin/env python
from __future__ import print_function
from lcatr import schema
schema.load_all()

def test_trivial():
    'A trivial test'

    row = dict(amp=1,
               gain=4.31,
               gain_error=0.01,
               psf_sigma=0.02)
    s = schema.get('fe55_analysis')
    data = schema.valid(s, **row)
    schema.write_file(data)

if '__main__' == __name__:
    test_trivial()
    print("test_trivial completed")
