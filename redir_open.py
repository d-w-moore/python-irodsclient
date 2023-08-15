import irods.test.helpers as helpers
import irods.keywords as kw

s = helpers.make_session()
o = s.data_objects.open(helpers.home_collection(s)+"/a.dat","w", **{
    kw.RESC_NAME_KW:'ptlocal'
    })
o.close()
