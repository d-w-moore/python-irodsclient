#!/bin/bash
[ -n "$1" ] || { echo >&2 "requires python_version as argument"; exit 1; }
set -e
DIR=$(dirname "$0")
cd "${DIR}"
echo "python_version=${1}" >.env
echo "repo_external=$(./print_repo_root_location)" >>.env

docker-compose -f harness-docker-compose.yml build
docker-compose -f harness-docker-compose.yml up -d
