import getopt,sys
from irods.ticket import Ticket
from irods.session import iRODSSession, _list
from irods.experimental.client.simple import Session
from irods.models import DataObject,Collection
from datetime import datetime as dt

optList,arg = getopt.getopt(sys.argv[1:],'Iv')
opts = dict(optList)
option_I_given = ('-I' in opts) # allow session cloning internal to open() call.

# Without -I optionmake a pre-existing session to "compete" with the one involved in the data open

if not option_I_given:
    s0 = Session(irods_env_file='/home/daniel/.irods/irods_environment.json')
    Ticket(s0,'myticket').supply()
    s0.pool.get_connection()
    if '-v' in opts: _list(s0,s0,session_class = type(s0))


s = Session(irods_env_file='/home/daniel/.irods/irods_environment.json')
Ticket(s,'myticket').supply()
if '-v' in opts: _list(s,s,session_class = type(s))

o = s.data_objects.open('/tempZone/home/rods/pwfile.txt', 'r',
                        allow_redirect=option_I_given # False value will prevent internal cloning of session
                        )
o.close()
