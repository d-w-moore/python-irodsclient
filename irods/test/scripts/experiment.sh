#!/bin/bash
DIR=$(dirname $0)
. $DIR/funcs
cd "$DIR"
set_up_ssl sudo -q
add_irods_to_system_pam_configuration
