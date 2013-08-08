#!/usr/bin/env python
'''
Test the summary_*.schema files.
'''

import os
import testing_common as tc
schema = tc.schema

def test_load():
    for name in [ "dark_gain", "dark_current", "dark_defective_columns",
                  "qe_analysis", "fe55_first_order","fe55_sextractor", ]:
        s = schema.get(name)
        assert s, 'failed to get schema %s' % name

def schema_field_line(sname, fields, line):
    if isinstance(fields, basestring):
        fields = fields.split()
    if isinstance(line, basestring):
        line = line.split()
    s = schema.get(sname)
    assert s, 'Failed to get schema "%s" for line %s' % (sname, line)
    d = {f:l for f,l in zip(fields, line)}
    r = schema.valid(s, **d)
    assert r, 'Failed to make a valid instance of "%s" with %s' % (sname, line)
    return r
    
def parse_fefo(line):
    fields = 'amp counts average noise_adu gain noise npix'
    return schema_field_line('fe55_first_order', fields, line)

def parse_fest(line):
    fields = 'amp Kafit_adu gain noise_adu noise_e sig_Ka npix difwid'
    return schema_field_line('fe55_sextractor', fields, line)

def parse_qe(line):
    fields = ['wavelength'] + ['amp%02dqe'%(x+1,) for x in range(16)]
    return schema_field_line('qe_analysis', fields, line)

class parse_dark(object):
    def __init__(self):
        self._parser = None
    def __call__(self, line):
        if line.startswith('amp# gain'):
            self._parser = self.parse_gain
            return None
        if line.startswith('amp# darkcur'):
            self._parser = self.parse_darkcur
            return None
        assert self._parser, 'parse_dark has no parser for %s' % line
        return self._parser(line)
    def parse_gain(self, line):
        fields = 'amp gain colhot hot_tot gt20'
        return schema_field_line('dark_gain', fields, line)

    def parse_darkcur(self, line):
        fields = 'amp darkcur cl90tile cl99tile cl999tile'
        return schema_field_line('dark_current', fields, line)
        
        
def parse_defective(line):
    fields = 'amp column'
    return schema_field_line('dark_defective_columns', fields, line)

def pick_parser(string):
    trigger = {
        'first order outputs from fe55': parse_fefo,
        'sextractor analysis': parse_fest,
        'QE analysis results': parse_qe,
        'number bias and expose frames': parse_dark(),
        'defective columns with more than 20 hot pix': parse_defective,
        }
    for t,p in trigger.items():
        if string.startswith(t):
            print 'Picking parser %s' % t
            return p

def parse_file(filename):
    ret = []
    parser = None
    with open(os.path.join(tc.test_dir, filename)) as fp:
        for line in fp.readlines():
            if line.startswith('amp#'):
                continue
            line = line.strip()
            if not line:
                continue
            p = pick_parser(line)
            if p:
                parser = p
                continue
            if not parser:
                print 'No parser for line:',line
            obj = parser(line)
            if not obj:
                if not line.startswith('amp#'):
                    print 'Warning, no object for line: %s' % line
                continue
            ret.append(obj)
    return ret

def _test_xxx(filename):
    outfile = os.path.splitext('test_summary_'+filename)[0] + '.json'
    data = parse_file(filename)
    assert data
    schema.save(data, outfile)
    try:
        data2 = schema.validate_file(outfile)
    except:
        print 'Failed to validate file %s' % outfile
        raise
    assert data2, 'Failed to validate %s' % outfile
    assert data == data2
    

def test_example_data():
    for what in 'fe55 qe dark'.split():
        _test_xxx('summary_%s.txt' % what)

if '__main__' == __name__:
    test_load()
    test_example_data()
