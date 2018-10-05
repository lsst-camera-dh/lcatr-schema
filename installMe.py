#!/usr/bin/env python
from __future__ import print_function
import sys
from argparse import ArgumentParser
from os.path import dirname,join,isdir, isfile
from os import makedirs
from shutil import copy,rmtree
from glob import glob

# packages should be installed under 
#  <root>/lib/pythonMAJ.MIN/site-packages
# where MAJ = sys.version_info.major and MIN = sys.version_info.minor


parser = ArgumentParser(description='install lcatr/schema')
parser.add_argument('jhRoot', action='store', metavar='root',
                    help='Root of job harness installation')
parser.add_argument('--update', '-u', action='store_true', dest = 'update',
                    default=False, 
                    help='allow overwrite of existing installation')

args = parser.parse_args()

jhRoot = vars(args)['jhRoot']
update = vars(args)['update']

pkg = 'lcatr/schema'
pythonversion = 'python' + str(sys.version_info.major) + '.' + str(sys.version_info.minor)
sitePkgs = join(jhRoot, 'lib', pythonversion, 'site-packages')
if (not isdir(sitePkgs)) or (not isdir(join(jhRoot, 'bin'))):
    print(root + ' is not root of a job harness installation')
    sys.exit()

pkgtop = dirname(sys.argv[0])

installedTop = join(sitePkgs, pkg)

if isfile(join(installedTop, '__init__.py')):
    if not update:
        print('Some version of the package is already installed')
        print('Delete or move away before attempting new install')
        print('or re-invoke with --update option')
        sys.exit()
    else:
        rmtree(installedTop)
        print('Old python files removed. Overwriting old version')


if not isdir(installedTop):
    makedirs(installedTop)


schemas = glob(join(pkgtop, 'schemas/*.org'))
for schema in schemas:
    copy(schema, join(jhRoot, 'schemas'))

srcs = glob(join(pkgtop, 'python', pkg, '*.py'))
for src in srcs:
    copy(src, installedTop)





