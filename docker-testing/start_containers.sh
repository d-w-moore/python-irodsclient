#!/bin/bash
set -e
DIR=$(dirname "$0")
cd "${DIR}"
echo "python_version=${1}" >.env
echo "repo_external=$(realpath ./repo)" >>.env
docker-compose -f harness-docker-compose.yml build
docker-compose -f harness-docker-compose.yml up -d
