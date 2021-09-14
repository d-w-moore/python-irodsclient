#!/usr/bin/env python
from __future__ import print_function
from irods.session import iRODSSession
import sys
import logging
import irods.keywords as kw
logging.basicConfig(level = logging.INFO)
import getopt

# repro285.py
# put a local file to a replica in irods, specified by DEST_RESC name
# usage: python ./repro285.py [-R DEST_RESC] filename

opt,arg = getopt.getopt(sys.argv[1:],'R:',['user=','zone=','pass=','host=','port='])

optD=dict(opt)

port_ = int(optD.get('--port','1247'))
host_ = optD.get('--host','localhost')
zone_ = optD.get('--zone','tempZone')
user_ = optD.get('--user','rods')
pass_ = optD.get('--pass')
assert type(pass_) is str

open1_opts={}

if '-R' in optD:
    open1_opts [kw.DEST_RESC_NAME_KW] = optD['-R']

objName = arg[0]

with iRODSSession(user=user_ , host=host_ , port=port_, zone=zone_ , password = pass_) as ses:
    fd1 = ses.data_objects.open(objName,'w',**open1_opts)
    token,hier = fd1.raw.replica_access_info()
    logging.info('token  = %s',token)
    logging.info('hier   = %s',hier)
    open2_opts = { kw.REPLICA_TOKEN_KW : token,
                   kw.DEST_RESC_HIER_STR_KW : hier,  
                   kw.RESC_HIER_STR_KW : hier        # read only ?
    }
    fd2 = ses.data_objects.open(objName,'a',finalize_on_close = False,**open2_opts)
    #print("{} {}".format(fd1.raw.conn,fd2.raw.conn))
    fd2.seek(4) ; fd2.write(b's\n')
    fd1.write(b'book')

    fd2.close()
    fd1.close()
    pass #1
pass #0
