#!/usr/bin/env python

import os
import hashlib

schema = [
    { 'schema_name':'fileref',
      'schema_version':0,
      "path": str,
      "sha1": str,
      "size": int,
      }]

def sha1sum(path):
    "Return the sha1 hexdigest of the contents of the given file."
    sha1 = hashlib.sha1()
    chunk_size = 128*sha1.block_size
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            sha1.update(chunk)
    return sha1.hexdigest()
    
def make(path):
    """
    Return a valid file reference data structure or raise ValueError.
    """
    try:
        s = os.stat(path)
    except OsError:
        raise ValueError, 'Can not stat "%s"' % path
    size = s.st_size

    import lcatr.schema
    return lcatr.schema.valid(schema[-1], 
                              path=path, size=size, sha1=sha1sum(path))
