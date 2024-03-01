#!/usr/bin/env bash

#TODO : RUN_AS_USER (default "") and KILL_TEST_CONTAINER (default 1) should be options

: ${KILL_TEST_CONTAINER:=1}
RUN_AS_USER=""

if [ "$1" = -u ]; then
    RUN_AS_USER="$2"
    shift 2
fi

if [ "$1" = "" ]; then
    echo >&2 "Usage: $0 /path/to/script"
    exit 1
fi

testscript=${1}
testscript_abspath=$(realpath "$testscript")
DIR=$(dirname $0)
cd $DIR

declare -A images=(
    [test_1.sh]=install-irods
    [test_2.sh]=bats-python3
    [test_3.bats]=bats-python3
    [experiment.sh]=ssl-and-pam
    [fail.sh]=ssl-and-pam
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
    docker exec $C grep '(0)' /tmp/irods_status 2>/dev/null >/dev/null
    [ $? -ne 0 ] && { echo -n . >&2; continue; }
    break
done

docker exec ${RUN_AS_USER:+"-u$RUN_AS_USER"} $C $INNER_MOUNT/$(realpath --relative-to $reporoot "$testscript_abspath")
STATUS=$?

# If KILL_TEST_CONTAINER is undefined, empty or zero-valued, don't kill container after script run, ie "leak" the container.
if [ $((0+KILL_TEST_CONTAINER)) -ne 0 ]; then
    echo >&2 'Killed:' $(docker stop --signal=KILL $C)
fi

exit $STATUS
