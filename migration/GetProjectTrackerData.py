'''=============================================================
c:/1work/Python/djcode/pjtk2/migration/GetProjectTrackerData.py
Created: 06 Nov 2013 11:16:47


DESCRIPTION:

 this script was written migrate tables in ProjectTrackerTables to a
 sqlite/django database.  It can be re-run anytime to
 refresh/syncronize the data in the sqlite file.

It first loads the look-up tables for databases, project types, lake,
as well as users and employee hierarchy.

Then it imports the project master list and inserts a record for each
project along with links to associated lookups.

Core project milestones are create for every project, although field
projects have different milestones that non-field projects.

All projects prior to 2010 are automatically signed off.  More recent
projects will have to be reviewed by employees and managers to ensure
that they are complete before being manuually approved.


A. Cottrill
=============================================================

'''

# *** NOTE ***
# Proj_Files and Proj_Photos are not included in this script (yet)


#===============================================================

import adodbapi
import datetime
import hashlib
import os
#import pdb
import shutil
import sqlite3
import re

from helper_functions import *


#here is the database we want to append into
#targdb = "c:/1work/DropBox/Dropbox/PythonStuff/djcode/uglmu/uglmu.db"
targdb = "C:/1work/Python/djcode/pjtk2/db/pjtk2.db"

# MEDIA_ROOT is where all of the files will be copied to this assumes
#that your app looks for files in a directory 'uploads' which located
#at the same level as ~/db (and ~/main, ~/static ~/static_root etc)
# make sure this matches MEDIA_ROOT in your django settings file
MEDIA_URL = 'reports'
MEDIA_ROOT = os.path.abspath(os.path.join(os.path.split(targdb)[0], "../uploads"))
MEDIA_PATH = os.path.abspath(os.path.join(MEDIA_ROOT, MEDIA_URL))

#here is the source database
#dbase = r"E:/Project_Tracking_Tables.mdb"
dbase = "C:/1work/Python/djcode/pjtk2/migration/Project_Tracking_Tables.mdb"

constr = 'Provider=Microsoft.Jet.OLEDB.4.0; Data Source={0}'.format(dbase)

my_user_id = get_user_id('adam', targdb)

#============================================
# get the database locations

# connect to the database
mdbconn = adodbapi.connect(constr)
# create a cursor
#try the lookup tables first - keep things simple
mdbcur = mdbconn.cursor()
# extract all the data
sql = """SELECT TL_DataLocations.MasterDatabase, TL_DataLocations.Path
FROM TL_DataLocations ORDER BY TL_DataLocations.ID"""

mdbcur.execute(sql)
result = mdbcur.fetchall()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

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
datalocs = zip(dbs, paths)

#open a connection to the sqlite database and append in
#the database locations:
sqlcon=sqlite3.connect(targdb)
sqlcur=sqlcon.cursor()

sql = """INSERT INTO [pjtk2_database] ("master_database","path") VALUES (?, ?);"""
sqlcur.executemany(sql, datalocs)
sqlcon.commit()
print datetime.datetime.now()
sqlcon.close()

#============================================
#now get the project type lookup table

sql = """SELECT Project_Type FROM TL_ProjType ORDER BY ID"""

mdbconn = adodbapi.connect(constr)
mdbcur = mdbconn.cursor()
mdbcur.execute(sql)
result = mdbcur.fetchall()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

# close the mdbcursor and connection
mdbconn.close()


#open a connection to the sqlite database and append in
#the database locations:
sqlcon=sqlite3.connect(targdb)
sqlcur=sqlcon.cursor()

sql = """INSERT INTO [pjtk2_projecttype] ("project_type") VALUES (?);"""
sqlcur.executemany(sql, result)
sqlcon.commit()
print datetime.datetime.now()
sqlcon.close()


# before we can add the master project list, we need to add
# a temporary field to hold the old primary key
sql = """ALTER TABLE pjtk2_project ADD COLUMN OldKey INT;"""
sqlcon=sqlite3.connect(targdb)
sqlcur=sqlcon.cursor()
sqlcur.execute(sql)
sqlcon.commit()

print datetime.datetime.now()
sqlcon.close()



#======================
#Lake

sqlcon=sqlite3.connect(targdb)
sqlcur=sqlcon.cursor()

sql = """INSERT INTO [pjtk2_lake] ("lake") VALUES ("Lake Huron");"""
sqlcur.execute(sql)
sqlcon.commit()
print datetime.datetime.now()
sqlcon.close()



#======================
#Employee Hierchy

csv_file = 'c:/1work/Python/djcode/pjtk2/migration/data/django_employees.csv'

#read the csv file into a list - comma separated with double quotes
employees = []
with open(csv_file, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        employees.append(row)            

print employees[:5]


for employee in employees:
    boss_id = get_user_id(employee[0])
    minion_id = get_user_id(employee[1])

    if boss_id:
        sqlcon=sqlite3.connect(targdb)
        sqlcur=sqlcon.cursor()
    
        sql = """INSERT INTO [pjtk2_employee] ("position", "role", "user_id", 
                 "supervisor_id") VALUES ("TBD", 3, ?,?);"""
        sqlcur.execute(sql, (minion_id, boss_id))
        sqlcon.commit()
        sqlcon.close()
   
print datetime.datetime.now()



#now we need to update the dba and managers

#David McLeish
user_id = get_user_id('mcleishda')
position = "Lake Manager"
role = '1'  #manager

sql = """Insert into pjtk2_employee (user_id, position, role)
      values ({0}, '{1}', {2})"""
sql = sql.format(user_id, position, role,)
update_db(sql)

#Chris Davis
user_id = get_user_id('davisch')
position = "Assessment Supervisor"
role = '1'  #manager

sql = "Update pjtk2_employee set position='{0}', role={1} where user_id={2}"
sql = sql.format(position, role, user_id)
update_db(sql)

#Dave Reid
user_id = get_user_id('reidda')
position = "Management Supervisor"
role = '1'  #manager

sql = "Update pjtk2_employee set position='{0}', role={1} where user_id={2}"
sql = sql.format(position, role, user_id)
update_db(sql)

    
#steve currie:
user_id = get_user_id('curriest')
position = "Data Management Coordinator"
role = '2'  #dba
sql = "Update pjtk2_employee set position='{0}', role={1} where user_id={2}"
sql = sql.format(position, role, user_id)
update_db(sql)


#======================
# Core Milestones

#here is the csv file of users, and user names:
csv_file = 'c:/1work/Python/djcode/pjtk2/migration/data/core_milestones.csv'

#read the csv file into a list - comma separated with double quotes
milestones = []
with open(csv_file, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        milestones.append(row)            

milestones[:5]

sqlcon=sqlite3.connect(targdb)
sqlcur=sqlcon.cursor()

sql = """INSERT INTO [pjtk2_milestone] ("id", "label", "category", "report",
    "protected", "order") VALUES (?,?,?,?,?,?);"""
sqlcur.executemany(sql, milestones)
sqlcon.commit()
print datetime.datetime.now()
sqlcon.close()
        


#======================
# Master Project List

# get the project tracker data from access

mdbconn = adodbapi.connect(constr)
mdbcur = mdbconn.cursor()
#the date is returned by a query called Make_pjtk2_project
mdbcur.callproc('Make_pjtk2_project')
result = mdbcur.fetchall()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

# close the mdbcursor and connection
mdbconn.close()

#before we can append the project master list, we have do some
#processing:
active = [x['active'] for x in result]
YEAR = [x['YEAR'] for x in result]
PRJ_DATE0 = [x['PRJ_DATE0'] for x in result]
PRJ_DATE1 = [x['PRJ_DATE1'] for x in result]
PRJ_CD = [x['PRJ_CD'] for x in result]
PRJ_NM = [x['PRJ_NM'] for x in result]
PRJ_LDR = [x['PRJ_LDR'] for x in result]
COMMENT0 = [x['COMMENT0'] for x in result]
MasterDatabase = [x['MasterDatabase'] for x in result]
ProjectType = [x['Project_Type'] for x in result]
FieldProject = [x['field_project'] for x in result]
owner = [x['owner'] for x in result]
dba = [x['dba'] for x in result]
oldKey = [x['oldKey'] for x in result]



#the comment field can't be null (but it is) - insert an empty string
#whenever it is null
COMMENT0 = [x if x is not None else " " for x in COMMENT0]

#we need user_id for the 'people' fields            
PRJ_LDR = [get_user_id(x) for x in PRJ_LDR]
owner = [get_user_id(x) for x in owner]
dba =  [get_user_id(x) for x in dba]

#we also need id numbers for the master databases and project types            
pjtype = [get_projtype_id(x) for x in ProjectType]                      
masterdb = [get_dbase_id(x) for x in MasterDatabase]

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
sqlcon=sqlite3.connect(targdb)
sqlcur=sqlcon.cursor()
args = result
#here is the sql to append project tracker data into sqlite:
sql = """INSERT INTO pjtk2_project ([active], [year], [prj_date0], [prj_date1],
      [prj_cd], [prj_nm], [prj_ldr_id], [comment], [master_database_id],
      [project_type_id], [field_project], [owner_id], [dba_id],[funding],
      [lake_id], [total_cost], [OldKey], [slug])
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?, 'Base', 1,0.00,?,?);"""

sqlcur.executemany(sql,args)
sqlcon.commit()
print datetime.datetime.now()
sqlcon.close()


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

print "Adding project-milestones..."            

#get all of our milestone ids
sqlcon = sqlite3.connect(targdb)
sqlcur = sqlcon.cursor()
sql = 'select id from pjtk2_milestone where category="Core"'
sqlcur.execute(sql)
result = sqlcur.fetchall()
sqlcon.close()

milestone_ids = [x[0] for x in result]

#get all of out project id numbers:
sqlcon = sqlite3.connect(targdb)
sqlcur = sqlcon.cursor()
sql = 'select id from pjtk2_project'
sqlcur.execute(sql)
result = sqlcur.fetchall()
sqlcon.close()
            
prj_ids = [x[0] for x in result]

            
for prj_id in prj_ids:
    sqlcon=sqlite3.connect(targdb)
    sqlcur=sqlcon.cursor()
    args = [(prj_id, x) for x in milestone_ids]            
    sql = """insert into pjtk2_projectmilestones (project_id, milestone_id, 
                required) values (?,?,1)"""
    sqlcur.executemany(sql,args)
    sqlcon.commit()

#update 'submitted' milestone for each project - if there in project
#tracker, they must have been submitted!
milestone_id = get_milestone_id('Submitted', targdb)
now = datetime.datetime.utcnow()

sqlcon=sqlite3.connect(targdb)
sqlcur=sqlcon.cursor()

sql = """update pjtk2_projectmilestones set completed=?
         where milestone_id=?"""
sqlcur.execute(sql, (now, milestone_id))
sqlcon.commit()

print "Done adding project-milestones!!"            

            

            
#============================================
#   REPORTS

# reports are a little trickier (completion presentations and summary
# reports are even more complicated and will be left until last)

# for each report in access tables, use Key_PM to find out which project it is appociated with,  the table that it is in will indicate which milestone it is for
# here is the psuedo code for the steps involved:

# get milestone_id from milestones where label==ms_access table name
# get project_id from pjtk2_project where oldkey=Key_PM            
            
# begin transaction
# select id from  pjtk2_projectsmilesones where
#            milestone_id={0} and project_id={1}

# copy report from Y to ~/medial/reports

# insert record into pjtk2_reports in
            
# create record in pjtk2_report_projectreport set
#            report_id=report_id and project_milestone_id to project_milestone_id

# update pjtk2_projectsmilesones set completed=now() where project 



#====================================
# COMPLETION PRESENTATIONS
          
# Now for each report table, import it from access, insert it into
#sqlite and then update the PM_KEY from OldKey to ID

#project completion presentations:
milestone_label = "Project Completion Pres."
milestone_id = get_milestone_id(milestone_label, targdb)

print "Starting to migrage {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id)

sql = """SELECT Proj_Comp_Pres.Key_PM, Proj_Comp_Pres.Report
     FROM Proj_Comp_Pres WHERE (((Proj_Comp_Pres.Report) Is Not Null))"""

result = msaccess(constr, sql)
print "{0} {1}s found.".format(result.numberOfRows, milestone_label)


key_pm = [x['key_pm'] for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row['report'])) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=my_user_id,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, targdb=targdb)

print "Done migrating {0}.".format(milestone_label)



#====================================
# COMPLETION REPORTS
          
# Now for each report table, import it from access, insert it into
#sqlite and then update the PM_KEY from OldKey to ID

#project completion presentations:
milestone_label = "Project Completion Report"
milestone_id = get_milestone_id(milestone_label, targdb)

print "Starting to migrage {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id)

sql = """SELECT Key_PM, Report FROM Proj_Completion
         WHERE (((Report) Is Not Null))"""

result = msaccess(constr, sql)
print "Record Count = %s" % result.numberOfRows

key_pm = [x['key_pm'] for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row['report'])) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=my_user_id,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, targdb=targdb)

print "Done migrating {0}.".format(milestone_label)


#====================================
#  PROJECT DESCRIPTIONS

milestone_label = "Project Description"
milestone_id = get_milestone_id(milestone_label, targdb)

print "Starting to migrage {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id)

sql = """SELECT Key_PM, Report FROM Proj_Descriptions
         WHERE (((Report) Is Not Null))"""

result = msaccess(constr, sql)
print "{0} {1}s found.".format(result.numberOfRows, milestone_label)

key_pm = [x['key_pm'] for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row['report'])) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=my_user_id,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, targdb=targdb)

print "Done migrating {0}.".format(milestone_label)


#====================================
#  PROJECT PROPOSAL PRESENTATIONS

milestone_label = "Project Proposal Presentation"
milestone_id = get_milestone_id(milestone_label, targdb)

print "Starting to migrage {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id)

sql = """SELECT Key_PM, Report FROM Proj_proposal_pres
    WHERE (((Report) Is Not Null))"""

result = msaccess(constr, sql)
print "Record Count = %s" % result.numberOfRows

key_pm = [x['key_pm'] for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row['report'])) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=my_user_id,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, targdb=targdb)

print "Done migrating {0}.".format(milestone_label)


#====================================
#  PROJECT PROPOSALs

milestone_label = "Project Proposal"
milestone_id = get_milestone_id(milestone_label, targdb)

print "Starting to migrage {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id)

sql = """SELECT Key_PM, Report FROM Proj_proposals
         WHERE (((Report) Is Not Null))"""

result = msaccess(constr, sql)
print "{0} {1}s found.".format(result.numberOfRows, milestone_label)


key_pm = [x['key_pm'] for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row['report'])) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=my_user_id,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, targdb=targdb)

print "Done migrating {0}.".format(milestone_label)


#====================================
#  FIELD PROTOCOLS

milestone_label = "Field Protocol"
milestone_id = get_milestone_id(milestone_label, targdb)

print "Migrating {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id)

sql = """SELECT Key_PM, Report FROM Proj_Protocols
         WHERE (((Report) Is Not Null))"""

result = msaccess(constr, sql)
print "{0} {1}s found.".format(result.numberOfRows, milestone_label)

key_pm = [x['key_pm'] for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row['report'])) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=my_user_id,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, targdb=targdb)

print "Done migrating {0}.".format(milestone_label)



#====================================
#  SUMMARY REPORTS

milestone_label = "Summary Report"
milestone_id = get_milestone_id(milestone_label, targdb)

print "Migrating {0}s (milestone_id = {1})".format(milestone_label,
                                                           milestone_id)

sql = """SELECT Key_PM, Report FROM Proj_summaries
      WHERE (((Report) Is Not Null))"""

result = msaccess(constr, sql)
print "{0} {1}s found.".format(result.numberOfRows, milestone_label)

key_pm = [x['key_pm'] for x in result]
#strip the extra strings off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row['report'])) for row in result]

for report in zip(key_pm, paths):
    migrate_reports(report[0],report[1], milestone_id, user_id=my_user_id,
                    media_url=MEDIA_URL, media_path=MEDIA_PATH, targdb=targdb)

print "Done migrating {0}.".format(milestone_label)
