from __future__ import print_function
from irods.test.helpers import home_collection, make_session
from irods.session import iRODSSession
from irods.path import cwd, rel_to_abs, chdir


# inject new methods into the iRODSSession class

iRODSSession.home = lambda self: self.collections.get(home_collection( self ))
iRODSSession.cwd = lambda self,*a,**kw:   cwd(self, *a, **kw)
iRODSSession.chdir = lambda self,*a,**kw: chdir(self, *a, **kw)
iRODSSession.abs = lambda self,*a,**kw:   rel_to_abs(self, *a, **kw)


# Search demo.
# Find lines in data objects starting at home collection that contain the searchString.

if __name__ == '__main__':

    searchString = b'xxx'

    s =  make_session()

    home = s.home()

    for d in home.subcollections:

        s.cwd(d.name)

        for o in d.data_objects:

            dname = s.abs(o.name)
            print (dname,end='\t')

            with s.data_objects.open(dname,'r') as f:
                print (
                      [(n+1,L) for n,L in (t for t in enumerate(f) if searchString in t[1])]
                )

        s.cwd('..')

