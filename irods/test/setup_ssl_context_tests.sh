#!/bin/bash
. $(dirname $0)/scripts/funcs
. $(dirname $0)/scripts/update_json_for_test

# This is mostly so we can call python3 as just "python"
activate_virtual_env_with_prc_installed >/dev/null 2>&1 || { echo >&2 "couldn't set up virtual environment"; exit 1; }

# Set up testuser with rods+SSL so we never have to run login_auth_tests.py as the service account.
iinit_as_rods >/dev/null 2>&1 || { echo >&2 "couldn't iinit as rods"; exit 2; }

original_script=/prc/$ORIGINAL_SCRIPT_RELATIVE_TO_ROOT

export RUN=$$:`date +%s`
export REPO=/prc
bats "$original_script"
