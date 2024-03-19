#!/bin/bash
set -e -x
PYTHON=$(which python3)
if [ -z "$PYTHON" ]; then
    PYTHON=$(which python)
fi
DIR=$(dirname "$0")
cd "$DIR"
$PYTHON ./recv_oneshot -h irods-catalog-provider -p 8888 -t 360
REPO="$(./print_repo_root_location)"
$PYTHON -m pip install "$REPO[tests]"
$PYTHON ./iinit.py \
    host irods-catalog-provider \
    port 1247 \
    user rods \
    password rods \
    zone tempZone

if [ -d /irods_shared ]; then
    groupadd -o irods $(stat -c%g /irods_shared)  # Appropriate the integer codes for irods group ...
    useradd irods $(stat -c%u /irods_shared)   # ... and user.
    mkdir /irods_shared/{tmp,reg_resc}
    chown irods.irods /irods_shared/{tmp,reg_resc}
    chmod 777 /irods_shared/reg_resc
    chmod g+ws /irods_shared/tmp
    useradd user -o -G irods -m -s/bin/bash
fi

su - user -c "$PYTHON '$REPO'/irods/test/runner.py"
