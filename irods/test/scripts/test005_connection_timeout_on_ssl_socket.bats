#!/usr/bin/env bats
#
# Test creation of .irodsA for iRODS pam_password authentication, this time purely internal to the PRC
# library code.

. "$BATS_TEST_DIRNAME"/test_support_functions
PYTHON=python3

# Setup/prerequisites are same as for login_auth_test.
# Run as ubuntu user with sudo; python_irodsclient must be installed (in either ~/.local or a virtualenv)
#

ALICES_PAM_PASSWORD=test123

setup()
{
    setup_pam_login_for_alice "$ALICES_PAM_PASSWORD"
}

teardown()
{
:
#   finalize_pam_login_for_alice
#   test_specific_cleanup
}

@test f001 {

    # Create and put into iRODS a large file which will take a significatnt fraction of a
    # second (>1e-5 on any CPU + Network combination) to checksum.

    LARGE_FILE=/tmp/largefile
    dd if=/dev/zero count=150k bs=1k of=$LARGE_FILE
    OUTPUT=$(python -ic "
import ssl
from irods.helpers import make_session, home_collection

ses=make_session()

coll = home_collection(ses)
ses.data_objects.put('$LARGE_FILE', coll)

if {type(conn.socket) for conn in ses.pool.idle | ses.pool.active} != {ssl.SSLSocket}:
    print('no connections')
    exit(1)
ses.connection_timeout = 1e-5
try:
    ses.data_objects.chksum(coll+'/$LARGE_FILE')
except Exception as e:
    print(type(e), 'thrown')
ses.connection_timeout = None
ses.data_objects.chksum(coll+'/$LARGE_FILE')
"
  )
  [[ $OUTPUT =~ NetworkException.*thrown ]]
}
