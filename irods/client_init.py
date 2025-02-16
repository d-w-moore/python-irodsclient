#!/usr/bin/env python3

import contextlib
import getopt
import getpass
import os
import sys
import textwrap

from irods import env_filename_from_keyword_args, derived_auth_filename
import irods.client_configuration as cfg
import irods.password_obfuscation as obf
import irods.helpers as h


@contextlib.contextmanager
def _open_file_for_protected_contents(file_path, *arg, **kw):
    f = old_mask = None
    try:
        old_mask = os.umask(0o77)
        f = open(file_path, *arg, **kw)
        yield f
    finally:
        if old_mask is not None:
            os.umask(old_mask)
        if f is not None:
            f.close()


class irodsA_already_exists(Exception):
    pass


def _write_encoded_auth_value(auth_file, encode_input, overwrite):
    if not auth_file:
        raise RuntimeError(f"Path to irodsA ({auth_file}) is null.")
    if not overwrite and os.path.exists(auth_file):
        raise irodsA_already_exists(
            f"Overwriting not enabled and {auth_file} already exists."
        )
    with _open_file_for_protected_contents(auth_file, "w") as irodsA:
        irodsA.write(obf.encode(encode_input))


def write_native_irodsA_file(password, overwrite=True, **kw):
    """Write the credentials to an .irodsA file that will enable logging in with native authentication
    using the given cleartext password.

    If overwrite is False, irodsA_already_exists will be raised if an .irodsA is found at the
    expected path.
    """
    env_file = env_filename_from_keyword_args(kw)
    auth_file = derived_auth_filename(env_file)
    _write_encoded_auth_value(auth_file, password, overwrite)


# Reverse compatibility.
write_native_credentials_to_secrets_file = write_native_irodsA_file


# Facility for writing authentication secrets file.  Designed to be useable for iRODS 4.3(+) and 4.2(-).
def write_pam_irodsA_file(password, overwrite=True, ttl = '', **kw):
    import irods.auth.pam_password
    from irods.session import iRODSSession
    import io
    ses = kw.pop('_session', None) or h.make_session(**kw)
    if ses._server_version(iRODSSession.RAW_SERVER_VERSION) < (4,3):
        return write_pam_credentials_to_secrets_file(
            password,
            overwrite = overwrite,
            ttl = ttl,
            _session = ses)

    auth_file = ses.pool.account.derived_auth_file
    if not auth_file:
        msg = "Auth file could not be written because no iRODS client environment was found."
        raise RuntimeError(msg)
    if ttl:
        ses.set_auth_option_for_scheme('pam_password', irods.auth.pam_password.AUTH_TTL_KEY, ttl)
    ses.set_auth_option_for_scheme('pam_password', irods.auth.FORCE_PASSWORD_PROMPT, io.StringIO(password))
    ses.set_auth_option_for_scheme('pam_password', irods.auth.STORE_PASSWORD_IN_MEMORY, True)
    L = []
    ses.set_auth_option_for_scheme('pam_password', irods.auth.CLIENT_GET_REQUEST_RESULT, L)
    with ses.pool.get_connection() as conn:
        _write_encoded_auth_value(auth_file, L[0], overwrite)


def write_pam_credentials_to_secrets_file(password, overwrite=True, ttl = '', **kw):
    """Write the credentials to an .irodsA file that will enable logging in with PAM authentication
    using the given cleartext password.

    If overwrite is False, irodsA_already_exists will be raised if an .irodsA is found at the
    expected path.
    """
    s = kw.pop('_session', None) or h.make_session(**kw)
    s.pool.account.password = password
    to_encode = []
    with cfg.loadlines(
        [
            dict(setting="legacy_auth.pam.password_for_auto_renew", value=None),
            dict(setting="legacy_auth.pam.store_password_to_environment", value=False),
            dict(setting="legacy_auth.pam.time_to_live_in_hours", value = ttl)
        ]
    ):
        to_encode = s.pam_pw_negotiated
    if not to_encode:
        raise RuntimeError(f"Password token was not passed from server.")
    auth_file = s.pool.account.derived_auth_file
    _write_encoded_auth_value(auth_file, to_encode[0], overwrite)


if __name__ == "__main__":
    extra_help = textwrap.dedent(
        """
    This Python module also functions as a script to produce a "secrets" (i.e. encoded password) file.
    Similar to iinit in this capacity, if the environment - and where applicable, the PAM
    configuration for both system and user - is already set up in every other regard, this program
    will generate the secrets file with appropriate permissions and in the normal location, usually:

       ~/.irods/.irodsA

    The user will be interactively prompted to enter their cleartext password.
    """
    )

    vector = {
        "pam_password": write_pam_irodsA_file,
        "native": write_native_irodsA_file
    }
    opts, args = getopt.getopt(sys.argv[1:], "-h", ["ttl=","help"])
    optD = dict(opts)
    help_selected = {*optD} & {'-h','--help'}
    if len(args) != 1 or help_selected:
        print("{}\nUsage: {} [-h | --help | --ttl HOURS] AUTH_SCHEME".format(extra_help, sys.argv[0]))
        print("  AUTH_SCHEME:")
        for x in vector:
            print("    {}".format(x))
        sys.exit(0 if help_selected else 1)
    elif args[0] in vector:
        options = {}
        if '--ttl' in optD:
            options['ttl'] = optD['--ttl']
        vector[args[0]](getpass.getpass(prompt=f"{args[0]} password: "), **options)
    else:
        print("did not recognize authentication scheme argument", file=sys.stderr)
