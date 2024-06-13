#!/bin/bash
set -e -x
PYTHON=$(which python3)
if [ -z "$PYTHON" -o $PYTHON_VERSION '<' 3 ]; then
    PYTHON=$(which python)
fi
DIR=$(dirname "$0")
cd "$DIR"
$PYTHON ./recv_oneshot -h irods-catalog-provider -p 8888 -t 360
REPO="$(./print_repo_root_location)"

NEW_REPO=/python-irodsclient
if cp -rp "$REPO" "$NEW_REPO"
then
    REPO="$NEW_REPO"
else
    echo >&2 "Warning: REPO='$REPO' unchanged from read-only mount.  Some features and tests may not work."
fi

$PYTHON -m pip install "$REPO[tests]"

if [ -d /irods_shared ]; then
    groupadd -o -g $(stat -c%g /irods_shared) irods      # Appropriate the integer codes for irods group ...
    useradd -g irods -u $(stat -c%u /irods_shared) irods # ... and user.
    mkdir /irods_shared/{tmp,reg_resc}
    chown irods.irods /irods_shared/{tmp,reg_resc}
    chmod 777 /irods_shared/reg_resc
    chmod g+ws /irods_shared/tmp
    useradd -G irods -m -s/bin/bash user
fi

su - user -c "\
$PYTHON '$DIR'/iinit.py \
    host irods-catalog-provider \
    port 1247 \
    user rods \
    password rods \
    zone tempZone
$PYTHON '$REPO'/irods/test/runner.py $*"
