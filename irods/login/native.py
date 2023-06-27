
def login(conn):
    conn._login_native()

# TODO : probably not needed, but interesting.
from . import X as X_base
class X(X_base):
        pass

