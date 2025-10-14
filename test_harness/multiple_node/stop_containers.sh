#!/bin/bash
set -e

# This script is launched on the docker host.

usage() {
  echo >&2 "usage: $0 irods_version"; exit 1;
}

if [ $# -eq 1 ]; then
    IRODS_VERSION=$1
    shift
else
    usage
fi


[ -n "$IRODS_VERSION" ] || {
     usage
}

IRODS_MAJOR=${IRODS_VERSION//.*/}

# In case the docker-compose setup varies between iRODS major releases, the .YML file may be a symbolic link.

docker compose -f harness-docker-compose-irods-${IRODS_MAJOR}.yml down
