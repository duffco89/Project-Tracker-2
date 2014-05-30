'''=============================================================
c:/1work/Python/djcode/pjtk2/migration/GetProjectTrackerData.py
Created: 06 Nov 2013 11:16:47


DESCRIPTION:

this script was written migrate tables in ProjectTrackerTables to a
Django database.  It can be re-run anytime to
refresh/syncronize the data in the sqlite file.

It first loads the look-up tables for databases, project types, lake,
as well as users and employee hierarchy.

Then it imports the project master list and inserts a record for each
project along with links to associated lookups.

Core project milestones are create for every project, although field
projects have different milestones than non-field projects.

All projects prior to 2010 are automatically signed off.  More recent
projects will have to be reviewed by employees and managers to ensure
that they are complete before being manually approved.

***  NOTE -  RUN ~/migration/get_django_users.py FIRST!!!  ***

Additionally, this script has been modified to run independently of
the django project and does not need access to django settings.  It is
python 3 compatible and can be run using system python (rather than a
virtual environment.)


A. Cottrill
=============================================================

'''


# *** NOTE ***
# Proj_Files and Proj_Photos are not included in this script (yet)


#===============================================================

#import adodbapi
import csv
import datetime
import hashlib
import os
#import pdb
import pyodbc
import shutil
#import sqlite3
import psycopg2
import re

from migration.helper_functions import *

BASE_DIR = 'c:/1work/Python/djcode/pjtk2/'
#this version of project track database as some specific queries and
#table needed to faciliate migration:
DBASE = "C:/1work/Python/djcode/pjtk2/migration/Project_Tracking_Tables.mdb"

# MEDIA_ROOT is where all of the files will be copied to this assumes
#that your app looks for files in a directory 'uploads' which is located
#at the same level as ~/db (and ~/main, ~/static ~/static_root etc)
# make sure this matches MEDIA_ROOT in your django settings file
MEDIA_URL = 'milestone_reports'
MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, "uploads"))
MEDIA_PATH = os.path.abspath(os.path.join(MEDIA_ROOT, MEDIA_URL))

MY_USER_ID = get_user_id('cottrillad', pg_constring)

#============================================
# POST GRES connection parameters

#pg connections parameters
con_pars = {'HOST': 'localhost',
          'NAME': 'pjtk2',
          'USER': 'adam',
          'PASSWORD': 'django'}

pg_constring = ("host='{HOST}' dbname='{NAME}' user='{USER}'" +
                  " password='{PASSWORD}'")
pg_constring = pg_constring.format(**con_pars)

#============================================
# get the database locations

#using pyodbc
constr = r"DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={0}".format(DBASE)
mdbconn = pyodbc.connect(constr)
mdbcur = mdbconn.cursor()

#try the lookup tables first - keep things simple
# extract all the data
sql = """SELECT TL_DataLocations.MasterDatabase, TL_DataLocations.Path
FROM TL_DataLocations ORDER BY TL_DataLocations.ID"""

mdbcur.execute(sql)
result = mdbcur.fetchall()

# verify that we got what we thought
for item in result[:5]:
    print(item)
print("Record Count = {}".format(len(result)))

# close the mdbcursor and connection
mdbcur.close()
mdbconn.close()

#pull the databases and their location out into lists
# and process them as necessary
dbs = [x[0] for x in result]
#strip the extra string off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row[1])) for row in result]

#put the elements to a list of tuples so that they can be appended
#with executemany
datalocs = list(zip(dbs, paths))

#open a connection to the sqlite database and append in
#the database locations:
pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()
sql = """INSERT INTO pjtk2_database ("master_database","path")
    VALUES (%s, %s);"""
pg_cur.executemany(sql, datalocs)
pg_conn.commit()
pg_conn.close()

print("Done uploading databases.")
print(datetime.datetime.now())


#============================================
#now get the project type lookup table

sql = """SELECT Project_Type FROM TL_ProjType ORDER BY ID"""

mdbconn = pyodbc.connect(constr)
mdbcur = mdbconn.cursor()
mdbcur.execute(sql)
result = mdbcur.fetchall()

# verify that we got what we thought
for item in result[:5]:
    print(item)
print("Record Count = {}".format(len(result)))

# close the mdbcursor and connection
mdbcur.close()
mdbconn.close()

#insert the project types into postgres
pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()
sql = """INSERT INTO pjtk2_projecttype ("project_type") VALUES (%s);"""
pg_cur.executemany(sql, result)
pg_conn.commit()
pg_conn.close()


# before we can add the master project list, we need to add
# a temporary field to hold the old primary key
sql = """ALTER TABLE pjtk2_project ADD COLUMN OldKey INT;"""
pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()
pg_cur.execute(sql)
pg_conn.commit()
pg_conn.close()

print("Done uploading project types.")
print(datetime.datetime.now())

#======================
#Lake

pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()
sql = """INSERT INTO pjtk2_lake (lake) VALUES (%s);"""
pg_cur.executemany(sql, [['Lake Huron'],['Lake Superior']])
pg_conn.commit()
pg_conn.close()


#======================
#Employee Hierchy

csv_file = 'c:/1work/Python/djcode/pjtk2/migration/data/django_employees.csv'
#read the csv file into a list - comma separated with double quotes
employees = []
with open(csv_file, 'rt') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        employees.append(row)
print(employees[:5])

pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()
#pg_cur.execute('SET CONSTRAINTS ALL DEFERRED')

for employee in employees[2:]:
    #boss_id = get_user_id(employee[0], pg_constring)
    boss_id = get_boss_id(employee[0], pg_constring)
    minion_id = get_user_id(employee[1], pg_constring)
    if boss_id:
        sql = """INSERT INTO pjtk2_employee (position, role, user_id,
                 supervisor_id) VALUES ('TBD', 3, %s, %s);"""
        pg_cur.execute(sql,[minion_id, boss_id])
    else:
        sql = """INSERT INTO pjtk2_employee (position, role, user_id)
                 VALUES ('TBD', 3, %s);"""
        pg_cur.execute(sql,[minion_id])
    pg_conn.commit()
pg_conn.close()
print(datetime.datetime.now())

#now we need to update the dba and managers
#David McLeish
user_id = get_user_id('mcleishda', pg_constring)
position = "Lake Manager"
role = '1'  #manager

sql = "Update pjtk2_employee set position='{0}', role={1} where user_id={2}"
sql = sql.format(position, role, user_id)

update_db(sql, pg_constring)


#Chris Davis
user_id = get_user_id('davisch', pg_constring)
position = "Assessment Supervisor"
role = '1'  #manager

sql = "Update pjtk2_employee set position='{0}', role={1} where user_id={2}"
sql = sql.format(position, role, user_id)
update_db(sql, pg_constring)

#Dave Reid
user_id = get_user_id('reidda', pg_constring)
position = "Management Supervisor"
role = '1'  #manager

sql = "Update pjtk2_employee set position='{0}', role={1} where user_id={2}"
sql = sql.format(position, role, user_id)
update_db(sql, pg_constring)

#steve currie:
user_id = get_user_id('curriest', pg_constring)
position = "Data Management Coordinator"
role = '2'  #dba
sql = "Update pjtk2_employee set position='{0}', role={1} where user_id={2}"
sql = sql.format(position, role, user_id)
update_db(sql, pg_constring)

print("Done uploading and updating employees.")

#======================
# Core Milestones

#here is the csv file of users, and user names:
csv_file = 'c:/1work/Python/djcode/pjtk2/migration/data/core_milestones.csv'

#read the csv file into a list - comma separated with double quotes
milestones = []
with open(csv_file) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        milestones.append(row)

milestones[:5]

pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()
sql = """INSERT INTO pjtk2_milestone (id, label, label_abbrev, category,
         report, protected, "order") VALUES (%s,%s,%s,%s,%s,%s,%s);"""
pg_cur.executemany(sql, milestones)
pg_conn.commit()
pg_conn.close()
print("Done uploading milestones.")
print(datetime.datetime.now())


#======================
# Master Project List

# get the project tracker data from access
mdbconn = pyodbc.connect(constr)
mdbcur = mdbconn.cursor()

#the date is returned by a query called Make_pjtk2_project
mdbcur.execute('exec Make_pjtk2_project')
result = mdbcur.fetchall()

# verify that we got what we thought
for item in result[:5]:
    print(item)
print("Record Count = {}".format(len(result)))

#check for any projects that our query might have missed (usually
#caused by a new user, project type or data location
project_codes = set([x.PRJ_CD for x in result])
mdbcur.execute('select distinct prj_cd from project_masterlist')
check = mdbcur.fetchall()
check=set([x[0] for x in check])
#the set difference should contain only place holders:
print("Missing project codes: " + '/n'.join(list(check-project_codes)))


# close the mdbcursor and connection
mdbconn.close()

#before we can append the project master list, we have do some
#processing:
active = [x.active for x in result]
YEAR = [x.Year for x in result]
PRJ_DATE0 = [x.PRJ_DATE0 for x in result]
PRJ_DATE1 = [x.PRJ_DATE1 for x in result]
PRJ_CD = [x.PRJ_CD for x in result]
PRJ_NM = [x.PRJ_NM for x in result]
PRJ_LDR = [x.PRJ_LDR for x in result]
COMMENT0 = [x.COMMENT0 for x in result]
MasterDatabase = [x.MasterDatabase for x in result]
ProjectType = [x.Project_Type for x in result]
FieldProject = [x.field_project for x in result]
owner = [x.owner for x in result]
dba = [x.dba for x in result]
oldKey = [x.oldKey for x in result]


#the comment field can't be null (but it is) - insert an empty string
#whenever it is null
COMMENT0 = [x if x is not None else " " for x in COMMENT0]

#we need user_id for the 'people' fields
PRJ_LDR = [get_user_id(x, pg_constring) for x in PRJ_LDR]
owner = [get_user_id(x, pg_constring) for x in owner]
dba =  [get_user_id(x, pg_constring) for x in dba]

#we also need id numbers for the master databases and project types
pjtype = [get_projtype_id(x, pg_constring) for x in ProjectType]
masterdb = [get_dbase_id(x, pg_constring) for x in MasterDatabase]

active = [True if x is -1 else False for x in active]
FieldProject = [True if x is -1 else False for x in FieldProject]

slug = [x.lower() for x in PRJ_CD]

prj_date0 = [x.strftime("%Y-%m-%d") for x in PRJ_DATE0]
prj_date1 = [x.strftime("%Y-%m-%d") for x in PRJ_DATE1]


#zip everything back into a list of tuples
# NOTE - PRJ_CD is duplicated to populate Slug to
result = zip(active, YEAR, prj_date0, prj_date1, PRJ_CD, PRJ_NM,
             PRJ_LDR, COMMENT0, masterdb, pjtype,
             FieldProject, owner, dba, oldKey, slug)

#reconnect to the target database and send in the master list
pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()

args = result
#here is the sql to append project tracker data into sqlite:
sql = """INSERT INTO pjtk2_project (active, year, prj_date0, prj_date1,
      prj_cd, prj_nm, prj_ldr_id, comment, master_database_id,
      project_type_id, field_project, owner_id, dba_id,funding,
      lake_id, total_cost, OldKey, slug)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, 'Base', 1,0.00,%s,%s);"""
pg_cur.executemany(sql, args)
pg_conn.commit()
pg_conn.close()
print("Done uploading projects.")
print(datetime.datetime.now())

#============================================
# to reload all of the reports in project tracker
# run the commands:
#   clear_upload_dir(MEDIA_PATH)
#   drop_report_tables(targdb)
# then from a command prompt (with venv active run syncdb)
# then exececute the code from this point down.

#============================================
#   Project-Milestones

#now for every project we want to insert a record into the core milestones table
#get the list of milestones:
print("Adding project-milestones...")

#get all of our milestone ids
pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()
sql = "select id from pjtk2_milestone where category='Core'"
pg_cur.execute(sql)
result = pg_cur.fetchall()
pg_conn.commit()
pg_conn.close()

milestone_ids = [x[0] for x in result]
#get all of out project id numbers:
pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()
sql = 'select id from pjtk2_project'
pg_cur.execute(sql)
result = pg_cur.fetchall()
pg_conn.commit()
pg_conn.close()

prj_ids = [x[0] for x in result]

pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()
for prj_id in prj_ids:
    args = [(prj_id, x) for x in milestone_ids]
    sql = """insert into pjtk2_projectmilestones (project_id, milestone_id,
                required) values (%s,%s,TRUE)"""
    pg_cur.executemany(sql, args)
pg_conn.commit()
pg_conn.close()

#update 'submitted' milestone for each project - if there in project
#tracker, they must have been submitted!
milestone_id = get_milestone_id('Submitted', pg_constring)
now = datetime.datetime.utcnow()

pg_conn = psycopg2.connect(pg_constring)
pg_cur = pg_conn.cursor()

sql = """update pjtk2_projectmilestones set completed=%s
         where milestone_id=%s"""
pg_cur.execute(sql, (now, milestone_id))
pg_conn.commit()

print("Done adding project-milestones!!")

#============================================
#   REPORTS

# reports are a little trickier (completion presentations and summary
# reports are even more complicated and will be left until last)

# for each report in access tables, use Key_PM to find out which
# project it is appociated with, the table that it is in will indicate
# which milestone it is for

#here is the psuedo code for the steps involved:

# get milestone_id from milestones where label==ms_access table name
# get project_id from pjtk2_project where oldkey=Key_PM

# begin transaction
# select id from  pjtk2_projectsmilesones where
#            milestone_id={0} and project_id={1}

# copy report from Y to ~/medial/reports

# insert record into pjtk2_reports in

# create record in pjtk2_report_projectreport set
# report_id=report_id and project_milestone_id to project_milestone_id

# update pjtk2_projectsmilesones set completed=now() where project

#====================================
# COMPLETION PRESENTATIONS

# Now for each report table, import it from access, insert it into
#sqlite and then update the PM_KEY from OldKey to ID
#project completion presentations:
milestone_label = "Project Completion Pres."
milestone_id = get_milestone_id(milestone_label, pg_constring)

print("Starting to migrate {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id))

sql = """SELECT Proj_Comp_Pres.Key_PM, Proj_Comp_Pres.Report
     FROM Proj_Comp_Pres WHERE (((Proj_Comp_Pres.Report) Is Not Null))"""
result = msaccess(constr, sql)
print("{0} {1}s found.".format(len(result), milestone_label))

key_pm = [x.Key_PM for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row.Report)) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=MY_USER_ID,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, pg_constring=pg_constring)
print("Done migrating {0}s.".format(milestone_label))

#====================================
# COMPLETION REPORTS

# Now for each report table, import it from access, insert it into
#sqlite and then update the PM_KEY from OldKey to ID

#project completion presentations:
milestone_label = "Project Completion Report"
milestone_id = get_milestone_id(milestone_label, pg_constring)

print("Starting to migrate {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id))

sql = """SELECT Key_PM, Report FROM Proj_Completion
         WHERE (((Report) Is Not Null))"""
result = msaccess(constr, sql)
print("Record Count = {}".format(len(result)))

key_pm = [x.Key_PM for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row.Report)) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=MY_USER_ID,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, pg_constring=pg_constring)

print("Done migrating {0}s.".format(milestone_label))

#====================================
#  PROJECT DESCRIPTIONS

milestone_label = "Project Description"
milestone_id = get_milestone_id(milestone_label, pg_constring)

print("Starting to migrate {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id))

sql = """SELECT Key_PM, Report FROM Proj_Descriptions
         WHERE (((Report) Is Not Null))"""
result = msaccess(constr, sql)
print("{0} {1}s found.".format(len(result), milestone_label))

key_pm = [x.Key_PM for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row.Report)) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=MY_USER_ID,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, pg_constring=pg_constring)

print("Done migrating {0}s.".format(milestone_label))


#====================================
#  PROJECT PROPOSAL PRESENTATIONS

milestone_label = "Project Proposal Presentation"
milestone_id = get_milestone_id(milestone_label, pg_constring)

print("Starting to migrate {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id))

sql = """SELECT Key_PM, Report FROM Proj_proposal_pres
    WHERE (((Report) Is Not Null))"""
result = msaccess(constr, sql)
print("Record Count = {}".format(len(result)))

key_pm = [x.Key_PM for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row.Report)) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=MY_USER_ID,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, pg_constring=pg_constring)

print("Done migrating {0}s.".format(milestone_label))

#====================================
#  PROJECT PROPOSALs

milestone_label = "Project Proposal"
milestone_id = get_milestone_id(milestone_label, pg_constring)

print("Starting to migrate {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id))

sql = """SELECT Key_PM, Report FROM Proj_proposals
         WHERE (((Report) Is Not Null))"""
result = msaccess(constr, sql)
print("{0} {1}s found.".format(len(result), milestone_label))

key_pm = [x.Key_PM for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row.Report)) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=MY_USER_ID,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, pg_constring=pg_constring)
print("Done migrating {0}s.".format(milestone_label))


#====================================
#  FIELD PROTOCOLS

milestone_label = "Field Protocol"
milestone_id = get_milestone_id(milestone_label, pg_constring)

print("Migrating {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id))

sql = """SELECT Key_PM, Report FROM Proj_Protocols
         WHERE (((Report) Is Not Null))"""

result = msaccess(constr, sql)
print("{0} {1}s found.".format(len(result), milestone_label))

key_pm = [x.Key_PM for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row.Report)) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=MY_USER_ID,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH,
                    pg_constring=pg_constring)

print("Done migrating {0}s.".format(milestone_label))

#====================================
#  SUMMARY REPORTS

milestone_label = "Summary Report"
milestone_id = get_milestone_id(milestone_label, pg_constring)

print("Migrating {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id))

sql = """SELECT Key_PM, Report FROM Proj_summaries
      WHERE (((Report) Is Not Null))"""
result = msaccess(constr, sql)
print("{0} {1}s found.".format(len(result), milestone_label))

key_pm = [x.Key_PM for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row.Report)) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=MY_USER_ID,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, pg_constring=pg_constring)
print("Done migrating {0}s.".format(milestone_label))


#====================================
#    ASSOCIATED FILES

#associated files are a little different that others because they are
#copies into project specific directories in
#'{MEDIA_ROOT}/associated_files' additionally, associated files are
#not associated with any particular milestones, just a project.
milestone_label = 'Associated Report'
ASSOC_ROOT = os.path.join(MEDIA_ROOT, 'associated_files')

#get list of associated files and their project codes
sql = ("SELECT PRJ_CD, Report FROM Project_MasterList " +
      "INNER JOIN Proj_Files ON Project_MasterList.Key_PM = Proj_Files.Key_PM"+
       " WHERE report IS NOT NULL")
result = msaccess(constr, sql)
print("{0} {1}s found.".format(len(result), milestone_label))

#create the directory for this project (if it does not already exist)
for rep in result:
    prj_cd = rep[0]
    src_path = rep[1].split(" # ")[0]
    if os.path.isfile(src_path) is False:
        msg = "{0} does not exist! ({1})".format(src_path, prj_cd)
        print(msg)
        log = open("./error.log", "a")
        log.write(msg + "\n")
        log.close()
    else:
        fname = os.path.split(src_path)[1]
        trg_dir = os.path.join(ASSOC_ROOT, prj_cd)
        if os.path.isdir(trg_dir) is False:
            os.makedirs(trg_dir)
        dest = os.path.join(trg_dir,fname)
        #copy the file into the directory
        move_report_file(src_path,dest)
        #create the appropriate record in the pjtk2 database.
        dest = dest.encode('utf-8')
        now = datetime.datetime.utcnow()
        try:
            pg_conn = psycopg2.connect(pg_constring)
            pg_cur = pg_conn.cursor()

            sql = 'select id from pjtk2_project where prj_cd=%s'
            #       select id from pjtk2_project where prj_cd='LHA_CF10_001'
            pg_cur.execute(sql, [prj_cd])
            project_id = pg_cur.fetchone()[0]

            args = dict(
                project_id = project_id,
                current = True,
                file_path = os.path.join(MEDIA_URL, 'associated_files', prj_cd,
                                           fname).replace("\\", "/"),
                uploaded_on = now,
                uploaded_by_id = str(MY_USER_ID),
                hash = hashlib.sha1(dest).hexdigest(),
            )

            sql = "INSERT INTO pjtk2_associatedfile({0}) values ({1})"
            sql = sql.format(
                ", ".join(args.keys()),
                ", ".join(['%s'] * len(args.keys())))
            pg_cur.execute(sql, list(args.values()))
            pg_conn.commit()
        except Exception as e:
            pg_conn.rollback()
            print("Error %s:" % e)
            sys.exit(1)
        finally:
            pg_conn.close()

print("Done migrating {0}s.".format(milestone_label))
