from irods.ticket import Ticket
from irods.session import iRODSSession, _list
from irods.experimental.client.simple import Session
from irods.models import DataObject,Collection
from datetime import datetime as dt
import sys


s = Session(irods_env_file='/home/daniel/.irods/irods_environment.json')
_list(s,s,session_class = type(s))
Ticket(s,'myticket').supply()

## q = s.query(Collection,DataObject)
## l = list(q)
## print(len(l))

# mode is Read("r") by default
mode = (sys.argv[1:]+['r'])[0]

o = s.data_objects.open('/tempZone/home/rods/pwfile.txt', mode,
                        allow_redirect=True
        )

print('got here',flush=True)

if mode == 'a':
 o.seek(0, 2)
 o.write(str(dt.now()).encode()+b"\n")
elif mode == 'r':
 print(o.read().decode())
o.close()
