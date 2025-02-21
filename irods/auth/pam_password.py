import getpass
import logging
import ssl
import sys
from . import (__NEXT_OPERATION__, __FLOW_COMPLETE__,
    AuthStorage,
    authentication_base, _auth_api_request,
    throw_if_request_message_is_missing_key,
    STORE_PASSWORD_IN_MEMORY, CLIENT_GET_REQUEST_RESULT, FORCE_PASSWORD_PROMPT)
from .native import _authenticate_native


AUTH_TTL_KEY = "a_ttl"


def login(conn, **extra_opt):
    context_opt =  {'user_name': conn.account.proxy_user,'zone_name': conn.account.proxy_zone}
    context_opt.update(extra_opt)
    _authenticate_pam_password(conn, req = context_opt)


_scheme = 'pam_password'


_logger = logging.getLogger(__name__)


def _authenticate_pam_password(conn, req):
    """The implementation for the client side of a pam_password scheme authentication flow.
       It is called by login(), the external-facing hook.
       Follow the pattern set in the original iRODS (native) plugin.
    """
    _logger.debug('----------- %s (begin)', _scheme)

    # By design, we persist this "depot" object over the whole of the authentication
    # exchange with the iRODS server as a means of sending password information to the
    # native phase of that process.  This has to be done in a way that preserves
    # the current environment (i.e. not writing to .irodsA) in the event that we
    # are authenticating without the help of iCommand-type client env/auth files.
    _ = AuthStorage.create_temp_pw_storage(conn)

    _pam_password_ClientAuthState(
        conn,
        scheme = _scheme
    ).authenticate_client(
        initial_request = req
    )

    _logger.debug('----------- %s (end)', _scheme)


def _get_pam_password_from_stdin(file_like_object = None):
    try:
        if file_like_object:
            if not getattr(file_like_object,'readline',None):
                msg = "The file_like_object, if provided, must have a 'readline' method."
                raise RuntimeError(msg)
            sys.stdin = file_like_object
        if sys.stdin.isatty():
            return getpass.getpass("Enter your current PAM password: ")
        else:
            return sys.stdin.readline().strip()
    finally:
        sys.stdin = sys.__stdin__


AUTH_PASSWORD_KEY = "a_pw"


class _pam_password_ClientAuthState(authentication_base):

    # Client define
    AUTH_CLIENT_AUTH_REQUEST = "pam_password_auth_client_request"

    # Server define
    AUTH_AGENT_AUTH_REQUEST = "auth_agent_auth_request"

    def __init__(self,*_,check_ssl=True,**_kw):
        super().__init__(*_,**_kw)
        self.check_ssl = check_ssl
        self._list_for_request_result_return = None

    def auth_client_start(self, request):

        # This list reference is popped and cached for the purpose of returning the request_result value
        # to the caller upon request.
        self._list_for_request_result_return = request.pop(CLIENT_GET_REQUEST_RESULT, False)

        if self.check_ssl:
            if not isinstance(self.conn.socket, ssl.SSLSocket):
                msg = "pam_password auth scheme requires secure communications (TLS/SSL) with the server."
                raise RuntimeError(msg)

        resp = request.copy()

        password_input_obj = resp.pop(FORCE_PASSWORD_PROMPT, None)

        if password_input_obj:
            if isinstance(password_input_obj,(int,bool)):
                password_input_obj = None
            # Like with the C++ plugin, we offer the user a chance to enter a password.
            resp[AUTH_PASSWORD_KEY] = _get_pam_password_from_stdin(file_like_object = password_input_obj)
        else:
            # Password from .irodsA in environment.
            if self.conn.account._auth_file:
                resp[__NEXT_OPERATION__] = self.perform_native_auth
                return resp

            # Password in cleartext form, fed in via iRODSSession constructor parameter.
            resp[AUTH_PASSWORD_KEY] = self.conn.account.password or ""

        resp[__NEXT_OPERATION__] = self.AUTH_CLIENT_AUTH_REQUEST
        return resp

    def pam_password_auth_client_request(self, request):
        server_req = request.copy()
        server_req[__NEXT_OPERATION__] = self.AUTH_AGENT_AUTH_REQUEST

        resp = _auth_api_request(self.conn, server_req)
        throw_if_request_message_is_missing_key(resp, {"request_result"})

        depot = AuthStorage.get_temp_pw_storage(self.conn)
        if depot:
            if resp.get(STORE_PASSWORD_IN_MEMORY, None):
                # Prevent use of an .irodsA to store an encoded password.
                depot.use_client_auth_file(None)
            depot.store_pw(resp["request_result"])
        else:
            msg = "auth storage object was either not set, or allowed to expire prematurely."
            raise RuntimeError(msg)

        if isinstance(self._list_for_request_result_return,list):
            self._list_for_request_result_return[:] = (resp["request_result"],)

        resp[__NEXT_OPERATION__] = self.perform_native_auth
        return resp

    def pam_password_auth_client_perform_native_auth(self, request):
        resp = request.copy()
        resp.pop(AUTH_PASSWORD_KEY, None)

        _authenticate_native(self.conn, request)

        resp["next_operation"] = __FLOW_COMPLETE__
        self.loggedIn = 1;
        return resp

    perform_native_auth = pam_password_auth_client_perform_native_auth
