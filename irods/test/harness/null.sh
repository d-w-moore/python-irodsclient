#!/bin/sh
PYTHON=`which python` || PYTHON=`which python3`
sudo apt update 
sudo apt install vim -y
sudo apt install iputils-ping -y
cp -rp /prc ~/prc
$PYTHON -m virtualenv ~/py3
. ~/py3/bin/activate
#$PYTHON -m pip install -e ~/prc
echo "python = $PYTHON"
