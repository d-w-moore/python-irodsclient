from irods.ticket import Ticket
from irods.session import iRODSSession, _list
from irods.experimental.client.simple import Session
from irods.models import DataObject,Collection
from datetime import datetime as dt


s = Session(irods_env_file='/home/daniel/.irods/irods_environment.json')
_list(s,s,session_class = type(s))
Ticket(s,'myticket').supply()
#q = s.query(Collection,DataObject)
#l = list(q)
#print(len(l))
o = s.data_objects.open('/tempZone/home/rods/pwfile.txt', 'a',
                        allow_redirect=True
        )
o.seek(0, 2)
o.write(str(dt.now()).encode()+b"\n")
o.close()
