#!/usr/bin/env bash
DIR=$(dirname $0)
cd $DIR
testscript=${1}
declare -A images=(
    [test_1.sh]=install-irods
    [test_2.sh]=bats-python3
)
image=${images[$(basename $testscript)]}
reporoot=$(realpath ./tests/repo)
#--------------
INNER_MOUNT=/prc
docker run \
    -v $reporoot:$INNER_MOUNT:ro \
    --rm \
    $image \
    $INNER_MOUNT/$(realpath --relative-to $reporoot $testscript)
