#!/bin/bash
DIR=$(dirname "$0")
cd "${DIR}"
echo "python_version=${1}" >.env
echo "repo_external=$(realpath "${DIR}/repo")" >>.env
docker-compose -f harness-docker-compose.yml up -d
