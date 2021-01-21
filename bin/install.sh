#!/usr/bin/env bash
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi
echo "installing dependencies"
apt-get install postgresql libpq-dev postgresql-client postgresql-client-common

echo "setting up the database"
sudo -u postgres createuser WD -dP

sudo -u postgres createdb wd-db

echo "installing python dependencies"
pip3 install -r ../requirements.txt

echo "Done!"