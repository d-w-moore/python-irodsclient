#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import socket
import posix
import shutil
from subprocess import (Popen, PIPE)

IRODS_SSL_DIR = '/etc/irods/ssl'
SERVER_CERT_HOSTNAME = None

def create_server_cert(process_output = sys.stdout, irods_key_path = 'irods.key', hostname = SERVER_CERT_HOSTNAME):
    p = Popen("openssl req -new -x509 -key '{irods_key_path}' -out irods.crt -days 365 <<EOF{_sep_}"
              "US{_sep_}North Carolina{_sep_}Chapel Hill{_sep_}UNC{_sep_}RENCI{_sep_}"
              "{host}{_sep_}anon@mail.com{_sep_}EOF\n""".format(
              host = (hostname if hostname else socket.gethostname()), _sep_ = "\n",**locals()),
        shell = True, stdout = process_output, stderr = process_output)
    p.wait()
    return p.returncode

def create_ssl_dir():
    save_cwd = os.getcwd()
    silent_run =  { 'shell': True, 'stderr' : PIPE, 'stdout' : PIPE }
    try:
        if not (os.path.exists(IRODS_SSL_DIR)):
            os.mkdir(IRODS_SSL_DIR)
        os.chdir(IRODS_SSL_DIR)
        Popen("openssl genrsa -out irods.key 2048",**silent_run).communicate()
        with open("/dev/null","wb") as dev_null:
            if 0 == create_server_cert(process_output = dev_null):
                Popen('openssl dhparam -2 -out dhparams.pem',**silent_run).communicate()
        return os.listdir(".")
    finally:
        os.chdir(save_cwd)

def test(optionD, args=()):
    if args: print ('warning: non-option args are ignored',file=sys.stderr)
    affirm = 'n' if os.path.exists(IRODS_SSL_DIR) else 'y'
    if '-f' not in optionD and affirm == 'n' and posix.isatty(sys.stdin.fileno()):
        try:
            input_ = raw_input
        except NameError:
            input_ = input
        affirm = input_("This will overwrite directory '{}'. Proceed(Y/N)? ".format(IRODS_SSL_DIR))
    if affirm[:1].lower() == 'y':
        shutil.rmtree(IRODS_SSL_DIR,ignore_errors=True)
        print("Generating new '{}'. This may take a while.".format(IRODS_SSL_DIR), file=sys.stderr)
        ssl_dir_files = create_ssl_dir()
        print('ssl_dir_files=', ssl_dir_files)
    
if __name__ == '__main__':
    import getopt
    opts, args = getopt.getopt(sys.argv[1:],'fh:')
    optD = dict(opts)
    SERVER_CERT_HOSTNAME = optD.get('-h')
    test(optD, args)
