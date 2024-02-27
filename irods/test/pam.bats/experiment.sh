#!/bin/bash
DIR=$(dirname $0)
. $DIR/funcs
cd "$DIR"; echo >&2 -n -- ; pwd
echo "setting up"
#$(up_from_script_dir 1)/setupssl.py
set_up_ssl sudo
