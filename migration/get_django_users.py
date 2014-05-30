'''=============================================================
c:/1work/Python/djcode/pjtk2/migration/get_django_users.py
Created: 06 Nov 2013 12:10:42

DESCRIPTION:

This scripts creates django users for each of the users in the csv
file ~/migraion/data/django_users.csv.  The csv file is create by the
access database [~\migration\Project_Tracking_Tables.mdb] and contains
one record for each project lead in project tracker (at least as of
today)

Employees who no longer work at UGLMU have their is_staff and is_active
flags set to false.  All other users have these flags set to True.  By
default, the password for all users is 'uglmu'

This script should be run before running ~/migration/GetProjectTrackerData.py

A. Cottrill
=============================================================

'''

import csv
import os

import django_settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

#here is the csv file of users, and user names:
csv_file = 'c:/1work/Python/djcode/pjtk2/migration/data/django_users.csv'

#read the csv file into a list - comma separated with double quotes
users = []
with open(csv_file, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        users.append(row)        

#loop over the users and create new user objects - if they are still
#staff, set their is_active and is_staff flags to true, otherwise false
for user in users:
    if user[3] == '1':
        status = True
    else:
        status = False
    new_user = User(username=user[0],
                first_name=user[1],
                last_name=user[2],
                password=make_password('uglmu'),
                is_active=status,
                is_staff=status,
            )
    new_user.save()


# steve Admin
steve = User(username='steve',
                first_name='Steve',
                last_name='currie',
                password=make_password('uglmu'),
                is_active=True,
                is_staff=True,
             is_superuser=True
            )
steve.save()
    
    
#so that we know we're done   
print "Done!"

#check:
all_users = User.objects.all()
for user in all_users[:6]:
    print user.first_name, user.last_name, user


    
