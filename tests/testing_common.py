#!/usr/bin/env python

import os, sys
test_dir = os.path.dirname(os.path.realpath(__file__))
top_dir = os.path.dirname(test_dir)

sys.path.insert(0,os.path.join(top_dir, 'python/lcatr'))
os.environ.setdefault('LCATR_SCHEMA_PATH', os.path.join(top_dir,'schemas'))

import schema
schema.load_all()

