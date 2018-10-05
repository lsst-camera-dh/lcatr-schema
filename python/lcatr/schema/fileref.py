#!/usr/bin/env python

import os
import hashlib
import json

schema = [
    { 'schema_name':'fileref',
      'schema_version':0,
      "path": str,
      "sha1": str,
      "size": int,
      "datatype": str,
      "metadata": str,
      }]

def sha1sum(path):
    "Return the sha1 hexdigest of the contents of the given file."
    sha1 = hashlib.sha1()
    chunk_size = 128*sha1.block_size
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            sha1.update(chunk)
    return sha1.hexdigest()

def make(path, datatype="LSSTSENSORTEST", metadata=None):
    """
    Return a valid file reference data structure or raise ValueError.
    """
    try:
        s = os.stat(path)
    except OSError as oserr:
        raise ValueError('Can not stat "%s"' % path)

    if metadata is not None and type(metadata) != dict:
        raise ValueError('fileref.make: metadata must be None or a dict object')

    size = s.st_size

    from . import valid
    return valid(schema[-1],
                 path=path, datatype=datatype, size=size,
                 metadata=json.dumps(metadata),
                 sha1=sha1sum(path))
