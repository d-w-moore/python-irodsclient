from irods.ticket import Ticket
from irods.session import iRODSSession, _list
from irods.experimental.client.simple import Session
from irods.models import DataObject,Collection

s = Session(irods_env_file='/home/daniel/.irods/irods_environment.json')
_list(s,s,session_class = type(s))
#exit()
Ticket(s,'myticket').supply()
q = s.query(Collection,DataObject)
l = list(q)
print(len(l))
