import irods

print('the tests have begun')

from irods.session import iRODSSession
with iRODSSession(host='localhost', port=1247, user='rods', password='rods', zone='tempZone') as session:
    coll = session.collections.get("/tempZone/home/rods")
    print('collection id', coll.id)

print('the tests are complete')

exit(0)
