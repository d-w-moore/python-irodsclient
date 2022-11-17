class iRODSAccess(object):

    def __init__(self, access_name, path, user_name='', user_zone='', user_type=None):
        self.access_name = access_name
        self.path = path
        self.user_name = user_name
        self.user_zone = user_zone
        self.user_type = user_type

    def __repr__(self):
        return "<iRODSAccess {access_name} {path} {user_name}({user_type}) {user_zone}>".format(**vars(self))
