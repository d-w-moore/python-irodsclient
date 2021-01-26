#!/usr/bin/env python2
import os
import atexit
from irods.session import iRODSSession

def get_session():
    session = None
    try:
        env_file = os.environ['IRODS_ENVIRONMENT_FILE']
    except KeyError:
        env_file = os.path.expanduser('~/.irods/irods_environment.json')
    session = iRODSSession(irods_env_file=env_file)
    atexit.register (lambda *_: session.cleanup())
    return session

if __name__ == '__main__':
    import sys
    path = sys.argv[1]
    s = get_session()
    with s.data_objects.open(path,'w+') as o:
      o.write('abcd')
      o.seek(-2, os.SEEK_CUR)
      x = o.read(1024)
      print ("read back =",x)
      pass
