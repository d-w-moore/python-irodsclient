from irods.ticket import Ticket
#from irods.session import iRODSSession as Session
from irods.experimental.client.simple import Session
from irods.models import DataObject,Collection

s = Session(irods_env_file='/home/daniel/.irods/irods_environment.json')
Ticket(s,'myticket').supply()
q = s.query(Collection,DataObject)
l = list(q)
print(len(l))
