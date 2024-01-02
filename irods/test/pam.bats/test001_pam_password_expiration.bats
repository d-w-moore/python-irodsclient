#!/usr/bin/env bats

. "$BATS_TEST_DIRNAME"/funcs
#

# requirements same as login_auth_test
# ubuntu user with sudo; python_irodsclient must be installed (can use a virtualenv)
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
    
    read -r -d '' SCRIPT <<-__end_python__
	import irods.test.helpers as h
	ses = h.make_session()
	ses.collections.get(h.home_collection(ses))
	print ('env_auth_scheme=%s' % ses.pool.account._original_authentication_scheme)
	__end_python__
    local OUTPUT=$(python -c "$SCRIPT")


[[ $OUTPUT =~ ^env_auth_scheme=pam_password$ ]]

    with_change_auth_params_for_test password_min_time 5 \
                                     password_min_time 6

    iinit <<<"$PASSWD"
    # Wait til password expires.
    sleep 8

    OUTPUT=$(python -c "$SCRIPT")
    [[ $OUTPUT =~ RuntimeError:${S}Time${S}To${S}Live ]] 

    with_change_auth_params_for_test password_max_time 3600

    OUTPUT=$(python -c "import irods.client_configuration as cfg
cfg.legacy_auth.pam.auto_renew_password = '$PASSWD'
cfg.legacy_auth.pam.time_to_live_in_hours = 1
$SCRIPT")

    [[ $OUTPUT =~ ^env_auth_scheme=pam_password$ ]]

}
