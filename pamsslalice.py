import sys
from irods.session import iRODSSession
import ssl
import getopt
import logging

from irods.test.login_auth_test_must_run_manually import pam_password_in_plaintext
import irods.client_configuration as cfg

ssl_settings =  {
               "client_server_negotiation": "request_server_negotiation",
               "client_server_policy": "CS_NEG_REQUIRE",
               "encryption_key_size": 32,
               "encryption_salt_size": 8,
               "encryption_num_hash_rounds": 16,
               "encryption_algorithm": "AES-256-CBC",
               "ssl_verify_server": "none",
}

USER='alice'
PASS='apass'

opt,arg = getopt.getopt(sys.argv[1:],'tlh:')
optD = dict(opt)

if optD.get('-l') is not None:
    cfg.legacy_auth.force_legacy_auth = True

if optD.get('-t') is not None:
  logging.warning('using empty ssl opts')
  ssl_settings = {}

ssl_settings.update(  { "authentication_scheme": "PAM", })

target_hostname = optD.get('-h','localhost')

with pam_password_in_plaintext():
  with iRODSSession(host=target_hostname, port=1247, user=USER, password=PASS, zone='tempZone', **ssl_settings) as session:
    coll = session.collections.get('/tempZone/home/alice')
    print(coll)
    print(coll.path)
    print(coll.id)
    print(coll.name)
    print(coll.metadata.items())
