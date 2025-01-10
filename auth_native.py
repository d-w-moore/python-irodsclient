import logging
logging.basicConfig( level = logging.INFO )

import irods.connection, irods.pool, irods.account

from irods.api_number import api_number
from irods.message import iRODSMessage, JSON_Message

class REQUEST_IS_MISSING_KEY(Exception): pass

def throw_if_request_message_is_missing_key( request, required_keys ):
  for key in required_keys:
    if not key in request:
      raise REQUEST_IS_MISSING_KEY(f'{key = }')

# General implementation to mirror iRODS cli/srv authentication framework

def _auth_api_request(conn, data):
    message_body = JSON_Message(data, conn.server_version)
    message = iRODSMessage('RODS_API_REQ', msg=message_body,
        int_info=api_number['AUTHENTICATION_APN']
    )
    conn.send(message)
    response = conn.recv()
    return response.get_json_encoded_struct()

class ClientAuthError(Exception):
    pass

FLOW_COMPLETE = "authentication_flow_complete"

# __ state machine with methods named for the operations valid on the client. __

class ClientAuthState:

    def __init__(self, connection, scheme):
        self.conn = connection
        self.loggedIn = 0
        self.scheme = scheme

    def call(self, next_operation, request):
        logging.info('next operation = %r', next_operation)
        func = getattr(self, next_operation, None)
        if func is None:
            raise RuntimeError("request contains no 'next_operation'")
        resp = func(request)
        logging.info('resp = %r',resp)
        return resp

    def authenticate_client(self, next_operation = "auth_client_start", initial_request = {}):

        to_send = initial_request.copy()
        to_send["scheme"] = self.scheme

        while True:
            resp = self.call(next_operation, to_send)
            if self.loggedIn:
                break
            next_operation = resp.get("next_operation")
            if next_operation is None:
              raise ClientAuthError("next_operation key missing; cannot determine next operation")
            if next_operation in (FLOW_COMPLETE,""):
              raise ClientAuthError("authentication flow stopped without success")
            to_send = resp
            
        logging.info("fully authenticated")
            
    def auth_client_authenticated(self, request):
        resp = request.copy()

        resp["next_operation"] = FLOW_COMPLETE
        self.loggedIn = 1;
        return resp


class native_ClientAuthState(ClientAuthState):

    AUTH_AGENT_START = 'native_auth_agent_start'

    def auth_client_start(self, request):
        resp = request.copy()
        # user_name and zone_name keys injected by authenticate_client() method
        resp["next_operation"] = self.AUTH_CLIENT_AUTH_REQUEST # native_auth_client_request
        return resp

    AUTH_AGENT_AUTH_REQUEST ='native_auth_agent_request'
    AUTH_CLIENT_AUTH_REQUEST = 'native_auth_client_request'
    AUTH_ESTABLISH_CONTEXT = 'native_auth_establish_context'

    def native_auth_client_request(self, request):
        server_req = request.copy()
        server_req["next_operation"] = self.AUTH_AGENT_AUTH_REQUEST

        resp = _auth_api_request(self.conn, server_req)

        resp["next_operation"] = self.AUTH_ESTABLISH_CONTEXT
        return resp

    AUTH_CLIENT_AUTH_RESPONSE = 'native_auth_client_response'

    def native_auth_establish_context(self, request):

        throw_if_request_message_is_missing_key(request,
            ["user_name", "zone_name", "request_result"])

_scheme = 'native'

account = irods.account.iRODSAccount(
  'localhost',1247,
  'rods','tempZone',
  irods_authentication_scheme = _scheme
)

pool = irods.pool.Pool(account)
connection = irods.connection.Connection(pool,account,connect = False)

state = native_ClientAuthState(
    connection, 
    scheme = _scheme
)

if __name__ == '__main__':
  state.authenticate_client(
    initial_request = {'user_name':account.client_user,
                       'zone_name':account.client_zone})
1;
