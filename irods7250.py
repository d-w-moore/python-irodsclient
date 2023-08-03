import getopt,sys,os
from irods.ticket import Ticket
from irods.session import iRODSSession, _list
from irods.experimental.client.simple import Session
from irods.models import DataObject,Collection
from datetime import datetime as dt

# Usage:
# issue7250.py [-v] [-g EXPLICIT_HOSTNAME ] -t TICKET_STRING PATH
# -v : call _list on original and cloned session
# -t : ticket string to use on both sessions
# -g : within this demo, -g supplies an hostname for the purpose of circumventing
#      data_objects.open()'s normal redirect.

optList,args = getopt.getopt(sys.argv[1:],'vg:t:')
opts = dict(optList)

CLIENT_CONFIG = os.path.expanduser('~/.irods/irods_environment.json')

sess = Session(irods_env_file = CLIENT_CONFIG)
Ticket(sess,opts['-t']).supply()

if '-v' in opts:
    _list(sess)

path = args[0]

#
# Inside of  sess.data_objects.open, GET_HOST_FOR_GET will be called unless -g was used
o = sess.data_objects.open(path, 'r',
                           returned_values = None if '-g' not in opts
                                                  else {'GET':opts['-g']})
o.close()
