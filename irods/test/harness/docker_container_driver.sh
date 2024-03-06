#!/usr/bin/env bash

KILL_TEST_CONTAINER=1
RUN_AS_USER=""
ECHO_CONTAINER=""

EXPLICIT_WORKDIR=""
while [[ $1  = -* ]]; do
    if [ "$1" = -c ]; then
        ECHO_CONTAINER=1
        shift
    fi
    if [ "$1" = -L ]; then
        KILL_TEST_CONTAINER=0
        shift
    fi
    if [ "$1" = -u ]; then
        RUN_AS_USER="$2"
        shift 2
    fi
    if [ "$1" = -w ]; then
        EXPLICIT_WORKDIR="$2"
        shift 2
    fi
done

if [ "$1" = "" ]; then
    echo >&2 "Usage: $0 [options] /path/to/script"
    echo >&2 "With options: [-L] to leak, [-u username] to run as non-root user"
    exit 1
fi

testscript=${1}
testscript_abspath=$(realpath "$testscript")
DIR=$(dirname $0)
cd $DIR
. ./test_script_parameters

image_basename=$(basename $testscript)
image=${images[$image_basename]}

if [ -z "$RUN_AS_USER" ]; then
    RUN_AS_USER=${user[$image_basename]}
fi

# Tests are run as testuser by default
: ${RUN_AS_USER:='testuser'}

WORKDIR=""
if [ -n "$EXPLICIT_WORKDIR" ]; then
    WORKDIR="$EXPLICIT_WORKDIR"
else
    WORKDIR=${workdirs[$RUN_AS_USER]}
fi

reporoot=$(realpath ./tests/repo)

INNER_MOUNT=/prc

# Start the container.
CONTAINER=$(docker run -d -v $reporoot:$INNER_MOUNT:ro --rm $image)

# Wait for iRODS and database to start up.
TIME0=$(date +%s)
while :; do
    [ `date +%s` -gt $((TIME0 + 30)) ] && { echo >&2 "Waited too long for DB and iRODS to start"; exit 124; }
    sleep 1 
    docker exec $CONTAINER grep '(0)' /tmp/irods_status 2>/dev/null >/dev/null
    [ $? -ne 0 ] && { echo -n . >&2; continue; }
    break
done

docker exec ${RUN_AS_USER:+"-u$RUN_AS_USER"} \
            ${WORKDIR:+"-w$WORKDIR"} \
            $CONTAINER \
            $INNER_MOUNT/$(realpath --relative-to $reporoot "$testscript_abspath")
STATUS=$?

if [ $((0+KILL_TEST_CONTAINER)) -ne 0 ]; then
    echo >&2 'Killed:' $(docker stop --signal=KILL $CONTAINER)
fi

[ -n "$ECHO_CONTAINER" ] && echo $CONTAINER
exit $STATUS
