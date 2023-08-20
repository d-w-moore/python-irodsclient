import irods.test.helpers as h
s = h.make_session()
l = h.iRODSUserLogins(s)
l.create_user("dan","d")
