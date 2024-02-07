#!/usr/bin/env bash

# IRODS_PACKAGE_VERSION if defined is like "4.3.1-0~bionic"
# (but contains no '~' suffix for irods versions <= 4.2.10)

BASE=$(basename "$0")
DIR=$(realpath "$(dirname "$0")")
cd "$DIR"
DOCKER=docker
for dockerfile in [0-9]*.Dockerfile; do 
    image_name=${dockerfile#[0-9]*_}
    image_name=${image_name%.Dockerfile}
    $DOCKER build -f $dockerfile -t $image_name . ${IRODS_PACKAGE_VERSION:+"--build-arg=irods_package_version=$IRODS_PACKAGE_VERSION"} \
                                                  ${NO_CACHE+"--no-cache"} || exit
done
