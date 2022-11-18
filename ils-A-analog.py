from irods.test.helpers import make_session
import  irods.exception
import sys
import getopt

s=make_session()

def get(p,ses=s):
    try:
        return ses.collections.get(p)
    except irods.exception.CollectionDoesNotExist:
        return ses.data_objects.get(p)

opt, arg = getopt.getopt(sys.argv[1:],'r')

raw = '-r' in dict(opt)

from pprint import pprint

L = []
for obj in arg:
    print('--',obj,'--')
    o=get(obj)
    i = s.permissions.get(o,report_raw_acls = raw)
    pprint(i)
    L.append(i)
