#!/bin/bash 

# a simple batch file to pull a git repository from my USB stick and
# get updated version of the database and media files too.  Ensures,
# to the greatest extent possible that the development environments
# remain consistent across platforms.

# push to the repository
git push usb --all

cp -r /home/adam/Documents/djcode/pjtk2/db /media/adam/AGM/pjtk2/db

# Copy the uploaded files:
cp -r /home/adam/Documents/djcode/pjtk2/uploads  /media/adam/AGM/pjtk2/uploads
