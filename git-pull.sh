#!/bin/bash 

# a simple batch file to pull a git repository from my USB stick and
# get updated version of the database and media files too.  Ensures,
# to the greatest extent possible that the development environments
# remain consistent across platforms.

# pull from the usb stick
git pull usb master

# get a fresh copy of the database:
cp -r /media/adam/AGM/pjtk2/db  /home/adam/Documents/djcode/pjtk2/db

# Copy the uploaded files:
cp -r /media/adam/AGM/pjtk2/uploads  /home/adam/Documents/djcode/pjtk2/uploads
                                     
