class Manager(object):

    __server_version = ()

    @property
    def server_version(self):
        if not self.__server_version:
            p = self.sess.pool
            if p is None : raise RuntimeError ("session not configured")
            conn = getattr(p,"_conn",None) or p.get_connection()
            if conn: self.__server_version = conn.server_version
        return tuple( self.__server_version )

    def __init__(self, sess):
        self.sess = sess

    def _set_manager_session(self, sess):
        self.sess = sess

'''
def _setup_for_limiting_connections():
    import gc
    # When sessions and managers go out of scope, clean them up with some urgency:
    gc.set_threshold(32)

_setup_for_limiting_connections()
'''
