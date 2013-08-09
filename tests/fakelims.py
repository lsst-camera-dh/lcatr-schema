#!/usr/bin/env python
"""
Let's pretend we are LIMS for the purpose of serving the /Schema/<commands>

This provides an HTTP server that tries mightly to pretend to be like
the real LIMS web app.

"""

import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import json
import time
import collections
from sys import stderr


import logging
logging.basicConfig(filename='fakelims.log',level=logging.DEBUG)

import shelve

def key_maker(n,v=None):
    return str(n+' '+str(v))
def key_name(key):
    return key.split()[0]

class FakeLimsDB(object):
    '''
    A fake LIMS database for testing the job harness.  
    '''

    def __init__(self, path):
        self.schema = shelve.open(path, writeback=True)

    def schema_register(self, schema):
        errors = 0
        for s in schema:
            key = key_maker(s['schema_name'], s.get('schema_version'))
            if self.schema.has_key(key):
                errors += 1
                continue
            self.schema[key] = s
        return errors

    def schema_match(self, name, version=None):
        if version is not None:
            key = key_maker(name,version)
            ret = self.schema.get(key)
            return ret

        match = []
        for key,s in self.schema.items():
            gotname, gotver = key.split()
            if gotname == name:
                match.append((gotver,s))

        if not match:
            return 
        return sorted(match)[-1][-1]

    def schema_all(self):
        return self.schema.values()

    pass

class FakeLimsCommands(object):
    
    # function: [expected, args]
    API = {
        'Schema/register': ['schema'],
        'Schema/all': [],
        'Schema/retrieve': ['match'],
        }

    def __init__(self):
        dbfile = os.path.splitext(__file__)[0] + '.db'
        self.db = FakeLimsDB(dbfile)
        return

    def __call__(self, base, cmd, **kwds):
        meth = eval('self.cmd_%s_%s'%(base,cmd))
        return meth(**kwds)

    def cmd_Schema_register(self, schema):
        nerr = self.db.schema_register(schema)
        if nerr:
            return {'error':'Failed to register %d schema' % nerr}
        return {'acknowledge': None}

    def cmd_Schema_all(self):
        return self.db.schema_all()

    def cmd_Schema_retrieve(self, match):
        return self.db.schema_match(**match)
    pass

lims_commands = FakeLimsCommands()

class FakeLimsHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        res = 'POST only, man!\n'
        self.wfile.write(res)
        return


    def postvars(self):
        """
        Return a dictionary of query parameters
        """
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        logging.debug('ctype="%s" pdict="%s"' % (str(ctype), str(pdict)))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            return {}
        query = {k:v[0] for k,v in postvars.iteritems()}
        js = query['jsonObject']
        return json.loads(js)

    def do_POST(self):

        # check against API - don't care about URL base, just command
        _,base,cmd = self.path.rsplit('/',2)
        base_cmd = base+'/'+cmd
        try:
            api = lims_commands.API[base_cmd]
        except KeyError:
            self.set_error('Unknown command: "%s"' % cmd)
            return

        pvars = self.postvars()
        chirp = 'CMD:"%s" POSTVARS:"%s"' % (base_cmd,pvars)
        print chirp
        logging.debug(chirp)

        required_params = set(api)
        if required_params and not required_params.issubset(pvars):
            msg = 'Required params: %s' % str(sorted(required_params))
            logging.error(msg)
            self.set_error(msg)
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

        ret = lims_commands(base, cmd, **pvars)
        print 'Lims returns:',str(ret)
        logging.debug('RET:%s'%str(ret))
        try:
            jstr = json.dumps(ret)
        except TypeError,msg:
            print 'Failed to dump to json for return from %s(%s)' % (base_cmd,str(pvars))
            raise
        self.wfile.write(jstr + '\n')
        return
        
    def set_error(self, msg):
        # use 412 for prereq not satisfied
        self.send_response(400)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(msg + '\n')
        return

    pass

def main():
    try:
        server = HTTPServer(('', 9876), FakeLimsHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()
if __name__ == '__main__':
    main()
