#!/usr/bin/env bats

. "$BATS_TEST_DIRNAME"/funcs
PYTHON=python3

# Setup/prerequisites are same as for login_auth_test.
# Run as ubuntu user with sudo; python_irodsclient must be installed (in either ~/.local or a virtualenv)
#

PASSWD=test123

setup()
{
    setup_pam_login_for_alice $PASSWD
}

teardown()
{
    finalize_pam_login_for_alice
}
 
@test f001 {

    local S="[[:space:]]" SCRIPT
    
    # Define core script to be run.

    local SCRIPT="
import irods.test.helpers as h
ses = h.make_session()
ses.collections.get(h.home_collection(ses))
print ('env_auth_scheme=%s' % ses.pool.account._original_authentication_scheme)
"
 
    # Test that the first run of the code in $SCRIPT allows normal authenticated operations to proceed normally.
    # (If authentication fails ses.collections.get will raise an exception.)

    local OUTPUT=$($PYTHON -c "$SCRIPT")

    [[ $OUTPUT =~ ^env_auth_scheme=pam_password$ ]]

    with_change_auth_params_for_test password_min_time 1 \
                                     password_max_time 1
 
     # Test that running the $SCRIPT raises an exception if the PAM password has expired.

    iinit <<<"$PASSWD"
    # Wait for password to expire.
    sleep 5
    echo "Running PYTHON script" >/dev/tty
    OUTPUT=$($PYTHON -c "$SCRIPT" 2>&1 >/dev/null || true)
    grep 'RuntimeError: Time To Live' <<<"$OUTPUT"
    
    # Test that the $SCRIPT, when run with proper settings, can successfully reset the password.

    with_change_auth_params_for_test password_max_time 3600

    OUTPUT=$($PYTHON -c "import irods.client_configuration as cfg
cfg.legacy_auth.pam.auto_renew_password = '$PASSWD'
cfg.legacy_auth.pam.time_to_live_in_hours = 1
$SCRIPT")

    [[ $OUTPUT =~ ^env_auth_scheme=pam_password$ ]]

}
