#!/usr/bin/env python

from __future__ import print_function
from lcatr.schema import fileref

def test_fileref():
    fr = fileref.make(__file__)
    print(fr)

if __name__ == '__main__':
    test_fileref()
