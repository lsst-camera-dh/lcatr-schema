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
    #print 'Added schema "%s" version %d' % (name, version)
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
    try:
        data = loads(string)
    except:
        print 'Failed to load schema file: %s' % filename
        raise

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
        s = json.dumps(obj, indent=2)
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
    if not schema:
        raise ValueError, 'Given empty schema along with: "%s' % str(kwds)

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
            raise ValueError, 'Missing required keyword argument: "%s" for schema "%s/%d"' % (name, schema['schema_name'], schema['schema_version'])

        dval = sval(dval)       # coerce given value into expected type

        ret[name] = dval
        continue
    
    return ret

def validate(data, strict = False):
    """
    Validate the given data structure against its schema.  If strict
    is True require that all values be of the required type, otherwise
    they must be merely convertable to the required type.
    """
    nam = data['schema_name']
    ver = data['schema_version']

    sch = get(nam,ver)
    if not sch:
        raise ValueError, 'No schema for "%s" version %s' % (nam, ver)
    dat = valid(sch, **data)    # throws if data is not valid enough
    if not strict: 
        return True
    if dat == data:
        return True
    raise ValueError, 'Data does not follow schema "%s" version %s' % (nam, ver)

def write_file(data, filename = 'summary.lims'):
    """
    Write the schema compliant data into the file.
    """
    if isinstance(data,dict):
        data = [data]
    towrite = []
    for d in data:
        s = get(d)
        d = valid(s,**d)        # be nice and allow coercion to correct types
        towrite.append(d)

    open(filename,'w').write(json.dumps(towrite, indent=2))


def validate_file(filename = "summary.lims"):
    """
    Validate the given named file against known schema and return its
    data or raise ValueError.
    """
    try:
        fp = open(filename)
    except IOError:
        print 'In: %s' % os.getcwd()
        raise
    sdata = fp.read()
    data = json.loads(sdata)
    for count, chunk in enumerate(data):
        try:
            validate(chunk)
        except :
            print "Chunk %d not valid: %s" % (count, str(chunk))
            raise
    return data

def _on_load():
    import fileref
    for s in fileref.schema:
        add(s)
    load_all()
_on_load()

