import getopt,sys,os
from irods.ticket import Ticket
from irods.session import iRODSSession, _list
from irods.experimental.client.simple import Session
from irods.models import DataObject,Collection
from datetime import datetime as dt

optList,args = getopt.getopt(sys.argv[1:],'Ivg:t:')
opts = dict(optList)
option_I_given = ('-I' in opts) # allow session cloning internal to open() call.

# Without -I optionmake a pre-existing session to "compete" with the one involved in the data open

CLIENT_CONFIG = os.expanduser('~/.irods/irods_environment.json')

if not option_I_given:
    s1 = Session(irods_env_file = CLIENT_CONFIG)
    Ticket(s1,opts['-t']).supply()
    s1.pool.get_connection()
    if '-v' in opts:
        _list(s1,s1,session_class = type(s1))

s2 = Session(irods_env_file = CLIENT_CONFIG)
Ticket(s2,opts['-t']).supply()
if '-v' in opts:
    _list(s2,s2,session_class = type(s2))

path = args[0] # TODO delete: was '/tempZone/home/rods/pwfile.txt'

o = s2.data_objects.open(path,
                        returned_values = None if ('-g' not in opts) else {'GET':opts['-g']},
                        allow_redirect = option_I_given # False value will prevent internal cloning of session
                        )
o.close()
