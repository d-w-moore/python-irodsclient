#!/usr/bin/env bash

testscript=${1}
testscript_abspath=$(realpath "$testscript")
DIR=$(dirname $0)
cd $DIR

declare -A images=(
    [test_1.sh]=install-irods
    [test_2.sh]=bats-python3
    [test_3.bats]=bats-python3

    [experiment.sh]=ssl-and-pam
)
image=${images[$(basename $testscript)]}
reporoot=$(realpath ./tests/repo)

INNER_MOUNT=/prc

# Start the container.
C=$(docker run -d -v $reporoot:$INNER_MOUNT:ro --rm $image)

# Wait for iRODS and database to start up.
TIME0=$(date +%s)
while :; do
    [ `date +%s` -gt $((TIME0 + 30)) ] && { echo >&2 "Waited too long for DB and iRODS to start"; exit 124; }
    sleep 1 
    docker exec $C grep '(0)' /tmp/irods_status 2>/dev/null
    [ $? -ne 0 ] && { echo -n . >&2; continue; }
    break
done

docker exec $C $INNER_MOUNT/$(realpath --relative-to $reporoot "$testscript_abspath")
STATUS=$?

# If undefined, empty or zero-valued, this environment variable allows leaking.
if [ $((0+LEAK_TEST_CONTAINERS)) -eq 0 ]; then
    echo >&2 'Killed:' $(docker stop --signal=KILL $C)
fi
exit $STATUS
