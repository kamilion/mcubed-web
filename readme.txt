#!/bin/bash
# Executable readme.txt file -- chmod +x and sudo me to do all this stuff for you.
# You're probably gonna need some stuff.
# Let's use python to get it.
apt-get install -y wajig apt-file
apt-file update

# First off, you'll need libssl-dev on ubuntu 13.xx for scrypt.
wajig install -y libssl-dev build-essential python-dev python-pip

# And get pip up to date so we have github support and --pre available
pip install --update pip virtualenv uwsgi supervisor

# Then you'll need to build a virtualenv.
virtualenv venv

# And activate it.
source venv/bin/activate

# Then pull down the rest of the packages with pip into the virtualenv.
pip install -r requirements.txt

# If you get problems with missing imports, uncomment this.
#pip install -r fullrequirements.txt

# If you get problems with python modules failing to compile due to missing headers,
# try something like the following to locate which packages have the missing file.
# wajig whichpkg aes.h
# This relies on apt-file being installed and up to date.

# And you should be good to go.
echo 'now you should check app/config.py and ./run.py if it is valid'
