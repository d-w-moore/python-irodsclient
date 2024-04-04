
def login(conn):
    conn.client_ctx = None
    conn._login_gsi()
