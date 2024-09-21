#!/bin/bash

echo "$0 running"
echo args:
for arg in $*; do
    echo $((++x)): "[$arg]"
done

sleep 3d
exit 118
