#!/usr/bin/env python

import json
from urllib import urlencode
from urllib2 import urlopen

import os

tests_dir = os.path.dirname(__file__)
pkg_dir = os.path.dirname(tests_dir)

from lcatr import schema
schema.load_all(os.path.join(pkg_dir,'schemas'))

lims_url = 'http://127.0.0.1:9876/Schema/'

type2str = {
    int: 'int',
    str: 'str',
    float: 'float',
}
str2type = dict(int=int,str=str,float=float)
    
def washed_schema():
    washed = []
    for s in reduce(lambda x,y:x+y, schema.store.values()):
        s = dict(s)             # copy
        for k in s.keys():
            v = s[k]
            if v in [int,str,float]:
                s[k] = type2str[v]
        washed.append(s)
    return washed

def test_register():
    washed = washed_schema()
    
    jdata = json.dumps(dict(schema=washed))
    qdata = urlencode({'jsonObject':jdata})
    url = lims_url + 'register'
    fp = urlopen(url, data=qdata)
    page = fp.read()
    print page

def test_all():
    jdata = json.dumps({})
    qdata = urlencode({'jsonObject':jdata})
    url = lims_url + 'all'
    fp = urlopen(url,data=qdata)
    page = fp.read()
    jdata = json.loads(page)
    print 'Got back %d schema:'%len(jdata)
    for i,s in enumerate(sorted(jdata, key=lambda x:(x['schema_name'],x['schema_version']))):
        print '#{i} v:{schema_version} {schema_name}'.format(i=i,**s)
    
def test_retrieve():
    for s in washed_schema():
        match = dict(name=s['schema_name'], version=s['schema_version'])
        jdata = json.dumps(dict(match=match))
        qdata = urlencode({'jsonObject':jdata})
        url = lims_url + 'retrieve'
        fp = urlopen(url,data=qdata)
        page = fp.read()
        jdata = json.loads(page)
        jdata.update(match)
        print 'Match: {name}/{version} --> {schema_name}/{schema_version}'.format(**jdata)
        


if '__main__' == __name__:
    test_register()
    test_all()
    test_retrieve()


        
