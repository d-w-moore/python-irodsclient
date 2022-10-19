#!/usr/bin/env python3
from irods.session import iRODSSession
from irods.test.helpers import home_collection
import os

# previously was using  an extra param keyword , make_ssl_context = True
#   but this might be better:

s = iRODSSession(irods_env_file = os.path.expanduser('~/.irods/irods_environment.json'), 
                 **{'ssl_context':'AUTO'}, # presence of the keyword with an object of the "wrong type"
                                           # (ie not SSLContext) but boolean 'True' invokes new SSLContext
                                           # auto-generation semantic.
                 )


h = home_collection(s)

print (s.collections.get(h))

