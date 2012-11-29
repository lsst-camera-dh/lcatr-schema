#!/usr/bin/env python
from glob import glob
from distutils.core import setup
setup(name='lcatr-schema',
      version='0',
      url='https://git.racf.bnl.gov/astro/cgit/lcatr/schema.git',
      author='Brett Viren',
      author_email='bv@bnl.gov',
      package_dir = {'': 'python'},
      packages = ['lcatr','lcatr.schema'],
      data_files = [('examples',glob('schemas/*.schema')),
                    ('doc',['doc/schema.org'])]
      )
