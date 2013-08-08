#!/usr/bin/env python

from lcatr import schema
schema.load_all()

def test_trivial():
    'A trivial test'

    row = dict(amp=1,
               counts=22330,
               average=376.2,
               noise_adu=2.1,
               gain=4.31,
               noise=9.1,
               npix=4.66)
    s = schema.get('fe55_first_order')
    data = schema.valid(s, **row)
    schema.write_file(data)

if '__main__' == __name__:
    test_trivial()
