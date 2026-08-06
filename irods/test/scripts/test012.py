#!/usr/bin/env python3

import getpass
import irods
import os
from unittest.mock import patch
from irods.auth import FORCE_PASSWORD_PROMPT

# Relies on preexisting irods_environment and certs copied from server:
#  {
#      "irods_authentication_scheme": "pam_interactive",
#      "irods_user_name": "john",
#      "_irods_user_name": "rods",
#      "irods_client_server_negotiation": "request_server_negotiation",
#      "irods_client_server_policy": "CS_NEG_REQUIRE",
#      "irods_connection_pool_refresh_time_in_seconds": 300,
#      "irods_cwd": "/tempZone/home/rods",
#      "irods_default_hash_scheme": "SHA256",
#      "irods_default_number_of_transfer_threads": 4,
#      "irods_default_resource": "demoResc",
#      "irods_encryption_algorithm": "AES-256-CBC",
#      "irods_encryption_key_size": 32,
#      "irods_encryption_num_hash_rounds": 16,
#      "irods_encryption_salt_size": 8,
#      "irods_home": "/tempZone/home/rods",
#      "irods_host": "localhost",
#      "irods_match_hash_policy": "compatible",
#      "irods_maximum_size_for_single_buffer_in_megabytes": 32,
#      "irods_port": 1247,
#      "irods_ssl_ca_certificate_file": "/home/daniel/tls_certs/irods_server.crt",
#      "irods_ssl_verify_server": "none",
#      "irods_transfer_buffer_size_for_parallel_transfer_in_megabytes": 4,
#      "irods_zone_name": "tempZone",
#      "schema_name": "service_account_environment",
#      "schema_version": "v5"
#  }

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

FIRST_PASSWORD = r'=i;r@o\d&s'
SECOND_PASSWORD = "otherrods"
TESTUSER = 'john'

with patch(
    'getpass.getpass',
    new_callable=getpass_new_callable(answers=[FIRST_PASSWORD,SECOND_PASSWORD])
):
    sess = irods.helpers.make_session(test_server_version=False)
    sess.set_auth_option_for_scheme('pam_interactive', FORCE_PASSWORD_PROMPT, True)
    home = sess.collections.get(f'/{sess.zone}/home/{sess.username}')

print(f'{home.path = }')
if home is None:
    exit(2)
if not home.path.endswith(f'/{TESTUSER}'):
    exit(1)
