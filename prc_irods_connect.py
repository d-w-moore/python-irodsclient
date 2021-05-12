from __future__ import print_function
from datetime import datetime
from irods.test.helpers import make_session
from irods.models import Collection
from time import sleep

INITIAL_SLEEP = 2

session = None
sleep(INITIAL_SLEEP)
try: 
    print (datetime.now(),end=' ')
    session = make_session()
    qresult = [row for row in 
               session.query(Collection.name).filter(Collection.name == '/{0.zone}/home/{0.username}'.format(session))]
except:
    print ("Python connection to iRODS provider ({0}) failed".format( session.host if session else "???"))
    exit(1)
else:
    if 1 == len(qresult): 
        print("Connection and test query succeeded")
    else:
        print("Connection possible but query failed to produce sane result.")
        exit(2)
