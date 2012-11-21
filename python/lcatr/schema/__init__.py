#!/usr/bin/env python
"""
Schema for result summaries
"""

import os
from glob import glob
import json

from collections import defaultdict

supported_types = { "int": int, "float":float, "str":str }
reserved_keys = ('schema_version','schema_name')

store = defaultdict(list)

def get(name, version = None):
    """
    Get a schema by name and optional version.  If version is None
    return higest versioned schema unless name is a compliant
    dictionary in which case get name and version from the schema_name
    and schema_version items in name.
    """
    if isinstance(name,dict) and version is None:
        data = name
        name = data['schema_name']
        version = data['schema_version']

    l = store[name]
    if not l: return
    if version is None: return l[-1]
    for s in l:
        if s['schema_version'] == version:
            return s
    return


def add(schema):
    """
    Add the schema to the store
    """
    # maintain order, if not efficiency
    name = schema['schema_name']
    version = schema['schema_version']

    exist = get(name,version)
    if exist:
        if exist == schema:
            return
        raise ValueError,'Differing schema for %s/%d already exists'%(name,version)

    lst = store[name]
    lst.append(schema)
    lst.sort(lambda a,b: cmp(a['schema_version'],b['schema_version']))
    store[name] = lst
    return


def loads(string):
    lines = []
    for line in string.split('\n'):
        sline = line.strip()
        if not sline: continue
        if sline.startswith('#'): continue
        lines.append(line)
    if not lines:
        return
    string = '\n'.join(lines)

    try:
        data = json.loads(string)
    except ValueError:
        data = None
    else:
        return data
        
    return eval(string)


def load(filename):
    """
    Load schema file
    """
    string = open(filename).read()
    data = loads(string)

    if not data:
        print 'Failed to load "%s"' % filename
        return

    if isinstance(data,dict):
        data = [data]

    def is_string(o):
        return isinstance(o,str) or isinstance(o,unicode)

    for d in data:
        tosave = {}
        for k,v in d.iteritems():
            if not k in reserved_keys:
                if is_string(v):
                    v = supported_types[v]
            tosave[k] = v
        add(tosave)
    return

def load_all(path = None):
    """
    Load all .schema files found in the given <path> list.

    If not <path> specified look for and use an LCATR_SCHEMA_PATH
    environment variable.
    """

    if not path:
        path = os.environ.get('LCATR_SCHEMA_PATH')
    if path:
        path = path.split(":")
    else:
        return

    for directory in path:
        for sfile in glob(os.path.join(directory,"*.schema")):
            load(sfile)
    return
  
def save(obj, filename, format = "JSON"):
    """
    Save <obj> to file named <filename> in given format ("JSON" by default)
    """
    if format == "Python":
        s = str(obj)
    else:
        s = json.dumps(obj)
    open(filename,'w').write(s)
    return

def valid(schema, **kwds):
    """
    Return a dictionary conforming to the given schema using data from
    the keyword arguments which must provide values of conforming
    type.  Any additional kwds are ignored.  If any of the keywords
    are found in lcatr.schema.reserved_keys they will be checked
    against the schema.  Any error raises ValueError.

    Note, the returned schema is not added.  See lcatr.schema.add() for that.
    """
    ret = {n:schema[n] for n in reserved_keys}
    for name, sval in schema.iteritems():
        dval = kwds.get(name, None)

        if name in reserved_keys: # skip or check if given
            if dval is None: 
                continue
            if sval != dval:
                raise ValueError,'Schema mismatch: %s differs: %s != %s' % \
                    (name, sval, dval)
            continue

        if dval is None:
            raise ValueError, 'Missing required keyword argument: "%s"' % name

        dval = sval(dval)       # coerce given value into expected type

        ret[name] = dval
        continue
    
    return ret

def write(data, filename = 'limssummary.json'):
    """
    Write the schema compliant data into the file.
    """
    if isinstance(data,dict):
        data = [data]
    towrite = []
    for d in data:
        s = get(d)
        d = valid(s,**d)
        towrite.append(d)

    open(filename,'w').write(json.dumps(towrite, indent=2))

def _on_load():
    import fileref
    for s in fileref.schema:
        add(s)
_on_load()

