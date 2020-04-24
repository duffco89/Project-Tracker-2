'''=============================================================
c:/1work/Python/djcode/pjtk2/pjtk2/utils/backup_pjkt2.py
Created: 16 Jul 2014 13:10:11

DESCRIPTION:

This script backs up the contents of pjtk2.  It is intended to be run
regularlly as a scheduled task.  It dumps the contents of the tables in
pjtk2 data bases (including tables users and tickets), and copies any
new or updated reports to the LRC server.

The sql dump of the databases tables (pjkt2.sql) can be used to create
a complete copy of the database by first create an new empty pjtk2
database (with gis extensions) followed by:

> psql -d pjtk2 -f pjtk2.sql

COMPLETE - commandline argument to control whether or not a full
back-up (ie all files) is performed, or just files uploaded since the
last backup.

A report of each backup is written to a log file (backup.log) in the
root of the target directory.

USAGE:
#complete backup
> python backup_ptjk2.py True
# partial backup - including only new uploads
> python backup_ptjk2.py False
# partial backup - including only new uploads (implicit)
> python backup_ptjk2.py


A. Cottrill
=============================================================

'''

from datetime import datetime
import logging
import psycopg2
import os
import shutil
import sys


#=====================
#      Constants

try:
    COMPLETE = sys.argv[1]
except IndexError:
    COMPLETE = False

#src_dir = 'C:/1work/Python/djcode/pjtk2/uploads'
src_dir = 'C:/1work/djcode/pjtk2/uploads'
trg_dir = 'Y:/Fisheries Management/Project Tracking/__backup'

if not os.path.exists(trg_dir):
    os.makedirs(trg_dir)

LOG_FILENAME = os.path.join(trg_dir, "backup.log")
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    )
TODAY = datetime.now().strftime("%d-%b-%y")

#=====================
#  Helper functions

def get_timestamp(trg_dir):
    """a little function to read a time stamp from a csv file placed in
    the target directory the last time we backed everything up.
    Returns None if a timestamp file cannot be found in the source
    directory, in which case all reports will be copied.

    Arguments:
    - `trg_dir`: where should we look for the time stamp file?

    """
    fname = os.path.join(trg_dir, 'timestamp.csv')
    try:
        with open(fname,'r') as f:
            ts = f.read()
    except:
        ts=None
    return(ts)


def write_timestamp(trg_dir):
    """another little helper file, write a timestamp out to a text file so
    that we know when everything was last backed up.

    Arguments:
    - `trg_dir`: where should we write the timestamp file?

    """
    from datetime import datetime

    now = datetime.now()
    fname = os.path.join(trg_dir, 'timestamp.csv')
    with open(fname,'w') as f:
        f.write(str(now))
    return(now)


def move_report_file(src_path, dest, trg_dir):
    '''a helper function used to move a file from the source directory to
    the destination directory. If the destination directory does not
    exist, it is created. If there is problem moving the file, an
    entry will be written in the log file.
    '''

    #make sure that the destination directory exists, if not create it
    dest_dir = os.path.dirname(dest)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    #now move the file
    try:
        shutil.copyfile(src_path, dest)
        return 0
    except IOError:
        if not os.path.exists(src_path):
            msg = "{} does not exist!\n".format(src_path)
        else:
            msg = "Warning - unable to copy {0} to {1}\n"
            msg = msg.format(src_path, dest)
        print(msg)
        logging.error(msg)
        return 1


#=====================================
#         INITIATE LOGFILE

msg = "Starting Project Tracker II - Backup ({})"
msg = msg.format(TODAY)
logging.info("=" * len(msg))
logging.info(msg)
logging.info('COMPLETE = {}'.format(COMPLETE))

#=====================================
#         DATABASE DUMP

os.system("set PGPASSWORD=django")

dump_file = '{0}/pjtk2.sql'.format(trg_dir)
shell_cmd = 'C:/gnu/pgsql/bin/pg_dump -U adam pjtk2 > "{}"'.format(dump_file)
os.system(shell_cmd)
print('Done dumping pjtk2 tables to {}'.format(dump_file))


#=====================================
#         FILE TRANSFER

#get list of reports uploaded since last backup:
#get the last backup timestamp.  If it doesn't exist, copy everything

ts = get_timestamp(trg_dir)

pgconstr = "dbname={0} user={1}".format('pjtk2', 'adam')
pgconn = psycopg2.connect(pgconstr)
pgcur = pgconn.cursor()

if ts and COMPLETE is False:
    #get just those reports that have been updated since the last time (ts)
    sql = ('select report_path from pjtk2_report where uploaded_on > ' +
           'timestamp %(ts)s')
    pgcur.execute(sql, {'ts':ts})
    reports = pgcur.fetchall()

    #now get the associated files
    sql = ('select file_path from pjtk2_associatedfile where uploaded_on > ' +
           'timestamp %(ts)s')
    pgcur.execute(sql, {'ts':ts})
    associated = pgcur.fetchall()
else:
# OR get them all
    sql = 'select report_path from pjtk2_report'
    pgcur.execute(sql)
    reports = pgcur.fetchall()

    #now get the associated files
    sql = 'select file_path from pjtk2_associatedfile'
    pgcur.execute(sql)
    associated = pgcur.fetchall()

pgcur.close()
pgconn.close()

#write an informative log message and start to transfer files
msg = "{} reports and {} associated files found."
msg = msg.format(len(reports), len(associated))
print(msg)
logging.info(msg)

if len(reports)>0:
    print ("Copying reports...")
    for rec in reports:
        fname = rec[0]
        src = os.path.join(src_dir, fname)
        dest = os.path.join(trg_dir, fname)
        move_report_file(src, dest, trg_dir)

if len(associated) > 0:
    print ("Copying associated files...")
    for rec in associated:
        fname = rec[0]
        #NOTE:this is a workaround for inconsistencies in uploads and MEDIA url
        #I have something mispecified in the settings - not sure what.
        fname = fname.replace('milestone_reports/','')
        src = os.path.join(src_dir, fname)
        dest = os.path.join(trg_dir, fname)
        move_report_file(src, dest, trg_dir)

print("Done copying files to {}".format(trg_dir))
msg = "Done Project Tracker II Backup ({})\n".format(TODAY)
logging.info(msg)

write_timestamp(trg_dir)
