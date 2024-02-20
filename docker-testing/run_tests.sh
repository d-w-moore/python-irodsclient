#!/bin/bash
set -e
DIR=$(dirname "$0")
cd "$DIR"
./recv_oneshot -h irods-provider -p 8888 -t 360
REPO="$(realpath ./repo)"
python -m pip install "$REPO[tests]"
./iinit.py \
    host irods-provider \
    port 1247 \
    user rods \
    password rods \
    zone tempZone
python "$REPO"/irods/test/runner.py