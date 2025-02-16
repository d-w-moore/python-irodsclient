from irods.session import iRODSSession
import irods.client_configuration as cfg

## -- Only for forcing 4.3 servers into obeying the old auth protocol & APIs
# cfg.legacy_auth.force_legacy_auth = True

with iRODSSession(user = 'rods', password = 'rods', 
                  zone = 'tempZone', host = 'localhost', port = 1247) as adm:
    if adm.raw_server_version() < (4,3):
        SCHEME = "pam"
    else:
        SCHEME = "pam_password"

CLIENT_OPTIONS_FOR_SSL = {
    "irods_client_server_policy": "CS_NEG_REQUIRE",
    "irods_client_server_negotiation": "request_server_negotiation",
    "irods_ssl_ca_certificate_file": "/etc/irods/ssl/irods.crt",
    "irods_ssl_verify_server": "cert",
    "irods_encryption_key_size": 16,
    "irods_encryption_salt_size": 8,
    "irods_encryption_num_hash_rounds": 16,
    "irods_encryption_algorithm": "AES-256-CBC",
}

ses = iRODSSession(
   user = 'alice', password = 'test123', zone = 'tempZone',
   host = 'localhost', port = 1247,
   authentication_scheme = SCHEME,
   **CLIENT_OPTIONS_FOR_SSL)

c = ses.collections.get("/tempZone/home/alice")
print(c.path)
