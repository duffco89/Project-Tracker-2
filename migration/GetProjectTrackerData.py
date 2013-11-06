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
import sqlite3
import datetime
import re
import pdb
import helper_functions

#here is the database we want to append into
#targdb = "c:/1work/DropBox/Dropbox/PythonStuff/djcode/uglmu/uglmu.db"
targdb = "C:/1work/Python/djcode/pjtk2/db/pjtk2.db"

#here is the source database
#dbase = r"E:/Project_Tracking_Tables.mdb"
dbase = "C:/1work/Python/djcode/pjtk2/migration/Project_Tracking_Tables.mdb"

constr = 'Provider=Microsoft.Jet.OLEDB.4.0; Data Source={0}'.format(dbase)

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



#now for every project we want to insert a record into the core milestones table
#get the list of milestones:
            


sqlcon = sqlite3.connect(targdb)
sqlcur = sqlcon.cursor()
sql = 'select id from pjtk2_milestone where category="Core"'
sqlcur.execute(sql)
result = sqlcur.fetchall()
sqlcon.close()

milestone_ids = [x[0] for x in result]

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
    sql = """insert into pjtk2_projectmilestones (project_id, milestone_id, required)
                values (?,?,1)
                """
    sqlcur.executemany(sql,args)
    sqlcon.commit()
print "done!!"            


            
            


            
#======================
# Now for each report table, import it from access, insert it into
#sqlite and then update the PM_KEY from OldKey to ID

#project completion presentations:
sql = """SELECT Proj_Comp_Pres.Key_PM, Proj_Comp_Pres.Report
FROM Proj_Comp_Pres WHERE (((Proj_Comp_Pres.Report) Is Not Null))"""
mdbconn = adodbapi.connect(constr)
mdbcur = mdbconn.cursor()
mdbcur.execute(sql)
result = mdbcur.fetchall()
mdbcur.close()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

Key_PM = [x[0] for x in result]
#strip the extra string off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row[1])) for row in result]

#put the elements to a list of tuples so that they can be appended
#with executemany
reportlocs = zip(Key_PM, paths, Key_PM)


InsertReportRecords(reportlocs, "pjtk2_proj_comp_pres", targdb,
                    "Report", True)


#====================================
#project completion presentations:
sql = """SELECT Key_PM, Report
FROM Proj_Completion WHERE (((Report) Is Not Null))"""
mdbconn = adodbapi.connect(constr)
mdbcur = mdbconn.cursor()
mdbcur.execute(sql)
result = mdbcur.fetchall()
mdbcur.close()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

Key_PM = [x[0] for x in result]
#strip the extra string off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row[1])) for row in result]
paths = [path.strip() for path in paths]
#put the elements to a list of tuples so that they can be appended
#with executemany
reportlocs = zip(Key_PM, paths, Key_PM)


InsertReportRecords(reportlocs, "pjtk2_proj_comp_pres",
                    targdb, "Report", True)


#====================================
#project descriptions:
reportTable = "pjtk2_proj_description"
sql = """SELECT Key_PM, Report
FROM Proj_Descriptions WHERE (((Report) Is Not Null))"""
mdbconn = adodbapi.connect(constr)
mdbcur = mdbconn.cursor()
mdbcur.execute(sql)
result = mdbcur.fetchall()
mdbcur.close()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

Key_PM = [x[0] for x in result]
#strip the extra string off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row[1])) for row in result]
paths = [path.strip() for path in paths]
#put the elements to a list of tuples so that they can be appended
#with executemany
reportlocs = zip(Key_PM, paths, Key_PM)

#insert the reports into sqlite:
#sqlcon=sqlite3.connect(targdb)
#sqlcur=sqlcon.cursor()


InsertReportRecords(reportlocs, "pjtk2_proj_description",
                    targdb, "Report", True)

#====================================
#project proposal presentations:
sql = """SELECT Key_PM, Report
FROM Proj_proposal_pres WHERE (((Report) Is Not Null))"""
mdbconn = adodbapi.connect(constr)
mdbcur = mdbconn.cursor()
mdbcur.execute(sql)
result = mdbcur.fetchall()
mdbcur.close()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

Key_PM = [x[0] for x in result]
#strip the extra string off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row[1])) for row in result]
paths = [path.strip() for path in paths]
#put the elements to a list of tuples so that they can be appended
#with executemany
reportlocs = zip(Key_PM, paths, Key_PM)


InsertReportRecords(reportlocs, "pjtk2_proj_proposal_pres",
                    targdb, "Report", True)


#====================================
#project proposals:
sql = """SELECT Key_PM, Report
FROM Proj_proposals WHERE (((Report) Is Not Null))"""
mdbconn = adodbapi.connect(constr)
mdbcur = mdbconn.cursor()
mdbcur.execute(sql)
result = mdbcur.fetchall()
mdbcur.close()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

Key_PM = [x[0] for x in result]
#strip the extra string off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row[1])) for row in result]
paths = [path.strip() for path in paths]
#put the elements to a list of tuples so that they can be appended
#with executemany
reportlocs = zip(Key_PM, paths, Key_PM)


InsertReportRecords(reportlocs, "pjtk2_proj_proposal",
                    targdb, "Report", True)



#====================================
#project Protocols:
sql = """SELECT Key_PM, Report
FROM Proj_protocols WHERE (((Report) Is Not Null))"""
mdbconn = adodbapi.connect(constr)
mdbcur = mdbconn.cursor()
mdbcur.execute(sql)
result = mdbcur.fetchall()
mdbcur.close()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

Key_PM = [x[0] for x in result]
#strip the extra string off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row[1])) for row in result]
paths = [path.strip() for path in paths]
#put the elements to a list of tuples so that they can be appended
#with executemany
reportlocs = zip(Key_PM, paths, Key_PM)

InsertReportRecords(reportlocs, "pjtk2_proj_protocols",
                    targdb, "Report", True)

#====================================
#project Summaries:
sql = """SELECT Key_PM, Report
FROM Proj_summaries WHERE (((Report) Is Not Null))"""
mdbconn = adodbapi.connect(constr)
mdbcur = mdbconn.cursor()
mdbcur.execute(sql)
result = mdbcur.fetchall()
mdbcur.close()

# verify that we got what we thought
for item in result[:5]:
    print item
print "Record Count = %s" % result.numberOfRows

Key_PM = [x[0] for x in result]
#strip the extra string off of the MS hyperlinks:
paths = [re.sub(r"\#.*","", str(row[1])) for row in result]
paths = [path.strip() for path in paths]
#put the elements to a list of tuples so that they can be appended
#with executemany
reportlocs = zip(Key_PM, paths, Key_PM)

InsertReportRecords(reportlocs, "pjtk2_proj_summaries",
                    targdb, "Report", True)
