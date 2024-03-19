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
cd ~
python "$REPO"/irods/test/runner.py
