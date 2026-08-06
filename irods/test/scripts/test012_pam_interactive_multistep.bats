#!/usr/bin/env bats

# The tests in this BATS module must be run as a (passwordless) sudo-enabled user.
# It is also required that the python irodsclient be installed under irods' ~/.local environment.

SKIP_IINIT_FOR_PASSWORD=yes

. $BATS_TEST_DIRNAME/test_support_functions

export TESTUSER="john"
export FIRST_PASSWORD="=i;r@o\\d&s" # somerods
export SECOND_PASSWORD="otherrods"

setup() {
  [ -f /tmp/test012_flag ] || {
      rm -fr ~/.irods
      /prc/test_harness/utility/iinit.py host localhost \
          port 1247     \
          zone tempZone \
          user rods     \
          password rods \

      sudo apt update 
      sudo apt install -y db-util libpam0g-dev

      ## Because iRODS 5+ negotiates for SSL automatically:
      CLIENT_JSON=~/.irods/irods_environment.json
      jq '.irods_client_server_policy="CS_NEG_REFUSE"' >$CLIENT_JSON.$$ <$CLIENT_JSON && \
      mv  $CLIENT_JSON.$$ $CLIENT_JSON

      sudo apt install irods-auth-plugin-pam-interactive-{client,server}

      setup_pam_login_for_user "${FIRST_PASSWORD}" $TESTUSER
      sudo cp $BATS_TEST_DIRNAME/files_for_test012/pam_password    /etc/pam.d/irods
      sudo cp $BATS_TEST_DIRNAME/files_for_test012/pam_interactive /etc/pam.d/
      sudo mkdir /t012 && sudo gcc -o /t012/pam_clear_token.so -fno-stack-protector -shared -fPIC $BATS_TEST_DIRNAME/files_for_test012/pam_clear_token.c

      db_file=/t012/pam_userdb.db
      sudo db_load -T -t hash "$db_file" <<<"${TESTUSER}"$'\n'"${SECOND_PASSWORD}"
      sudo chown root:root "$db_file"
      sudo chmod 600 "$db_file"

      # Tests require only the irods_environment.json
      rm -f ~/.irods/.irodsA

      ## Switch over to scheme to be tested.
      jq '.irods_authentication_scheme="pam_interactive"' >$CLIENT_JSON.$$ <$CLIENT_JSON && \
      mv  $CLIENT_JSON.$$ $CLIENT_JSON
  }
  touch /tmp/test012_flag
}

@test "pam_interactive_test_multistep_with_correct_passwords" {
:
python -c"
import getpass
import irods
import os
from unittest.mock import patch
from irods.auth import FORCE_PASSWORD_PROMPT

def getpass_new_callable(answers=()):
    class iterate_answers:
        def __init__(self,answers = answers):
            self.answers = answers
            self.count = 0
        def __call__(self,*_):
            count = self.count
            self.count += 1
            ans = self.answers[count]
            print ('*** giving answer:', ans)
            return ans
    return lambda : iterate_answers()

home = None

with patch(
    'getpass.getpass',
    new_callable=getpass_new_callable(answers=[os.environ['FIRST_PASSWORD'],os.environ['SECOND_PASSWORD']])
):
    sess = irods.helpers.make_session(test_server_version=False)
    sess.set_auth_option_for_scheme('pam_interactive', FORCE_PASSWORD_PROMPT, True)
    home = sess.collections.get(f'/{sess.zone}/home/{sess.username}')

if home is None:
    exit(2)
username = os.environ['TESTUSER']
if not home.path.endswith(f'/{username}'):
    exit(1)
"
}
