#!/usr/bin/env bash

#IRODS_VERSION="4.3.1-0~bionic"

BASE=$(basename "$0")
DIR=$(realpath "$(dirname "$0")")
cd "$DIR"
DOCKER=docker
for dockerfile in [0-9]*.Dockerfile; do 
    image_name=${dockerfile#[0-9]*_}
    image_name=${image_name%.Dockerfile}
    $DOCKER build -f $dockerfile -t $image_name . || exit
done

