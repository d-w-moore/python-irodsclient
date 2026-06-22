#!/usr/bin/env bats

# The tests in this BATS module must be run as a (passwordless) sudo-enabled user.
# It is also required that the python irodsclient be installed under irods' ~/.local environment.

SKIP_WRITING_PAM_CONFIG_FILE=""
SKIP_IINIT_FOR_PASSWORD=yes

. $BATS_TEST_DIRNAME/test_support_functions

setup() {
  [ -f /tmp/test012_flag ] || {
      rm -fr ~/.irods
      /prc/test_harness/utility/iinit.py host localhost \
          port 1247     \
          zone tempZone \
          user rods     \
          password rods \

      apt update 
      apt install -y db-util libpam0g-dev

      ## Because iRODS 5+ negotiates for SSL automatically:
      CLIENT_JSON=~/.irods/irods_environment.json
      jq '.irods_client_server_policy="CS_NEG_REFUSE"' >$CLIENT_JSON.$$ <$CLIENT_JSON && \
      mv  $CLIENT_JSON.$$ $CLIENT_JSON

      sudo apt install irods-auth-plugin-pam-interactive-{client,server}

      setup_pam_login_for_user "rods" $TESTUSER
      sudo cp $BATS_TEST_DIRNAME/files_for_test012/pam_interactive /etc/pam.d/irods
      sudo mkdir /t012 ; gcc -o /t012/pam_clear_token.so -fno-stack-protector -shared -fPIC $BATS_TEST_DIRNAME/files_for_test012/pam_clear_token.c

      # Tests require only the irods_environment.json
      rm -f ~/.irods/.irodsA

      ## Switch over to scheme to be tested.
      jq '.irods_authentication_scheme="pam_interactive"' >$CLIENT_JSON.$$ <$CLIENT_JSON && \
      mv  $CLIENT_JSON.$$ $CLIENT_JSON
  }
  touch /tmp/test012_flag
}

original_test_suite()
{
:
# local USER="alice"
# local PASSWORD="rods"
# sudo chpasswd <<<"$USER:$PASSWORD"
# python -m unittest irods.test.pam_interactive_test_must_run_manually
}

@test "original_pam_interactive_tests" {
  original_test_suite
}
