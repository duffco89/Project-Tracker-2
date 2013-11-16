'''=============================================================
c:/1work/Python/djcode/pjtk2/migration/Django_sqlite_to_pg.py
Created: 15 Nov 2013 14:38:55


DESCRIPTION:

This scripts uses the django orm to migrate data from an sqlite
database to postgres.  It essentailly emulates the scripts that
migrates data from access to sqlite.

To use this script, make sure that you run !/get_django_users.py first
to populate the users's table.  Once those users have been creates, it
should be just a matter of running this script to migrate the rest of
the data.

NOTE - the sister and family tables do not currently have any data and are not included in this migration (although a warning will be printed if those table do have data).  Additionally, the original project tracker did not have tags/keywords.  Any keywords that exists in the sqlite database are not transfered at this time.


A. Cottrill
=============================================================

'''



import os
import sqlite3
import psycopg2
from datetime import datetime
import pytz

os.getcwd()
os.chdir(os.path.split(os.getcwd())[0])
import django_settings


from pjtk2.models import *
from taggit.models import Tag


#here is the database we want to get the data out of:
sqlite = "C:/1work/Python/djcode/pjtk2/db/pjtk2.db"


def get_records(tbl, db, quiet=True):
    '''a little helper function to retrieve all of the records and
    field names in tbl from the database db.  If quiet is false, the
    function will also report the number of records returned and the
    field names.
    '''

    sqlcon=sqlite3.connect(db)
    sqlcon.row_factory = sqlite3.Row
    sqlcur=sqlcon.cursor()
    sql = "SELECT * FROM {0} order by id".format(tbl)
    sqlcur.execute(sql)
    fields = list(map(lambda x: x[0], sqlcur.description))
    records = sqlcur.fetchall()
    sqlcon.close()
    if not quiet:
        print "{0} records returned".format(len(records))
        print "Fields in {0}:".format(tbl)
        for fld in fields:
            print "\t{0}".format(fld)        
    return {'records':records, 'fields':fields}
    

def build_fields(fields):
    '''Another little helper - takes a list of field names and creates
    model specification string for a django object with those
    fields. - just cut and paste the output back into your script.
    '''
    out = []
    for fld in fields:
        out.append("{0} = row['{0}'],".format(fld))
    out = "\n\t".join(out)
    print "\t" + out




    


    
#=========================
#      DATABASES

tbl = 'pjtk2_database'
result = get_records(tbl, sqlite)        
  
for row in result['records']:
    item = Database(
        master_database = row['master_database'],
        path = row['path']
    )
    item.save()


now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))


#=========================
#      LAKES

tbl = 'pjtk2_lake'
result = get_records(tbl, sqlite)        
  
for row in result['records']:
    item = Lake(
        lake = row['lake'],
    )
    item.save()


now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))


#=========================
#      Project Types

tbl = 'pjtk2_projecttype'
result = get_records(tbl, sqlite)        
  
for row in result['records']:
    item = ProjectType(
        project_type = row['project_type'],
    )
    item.save()


now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))



#=========================
#      Milestones

tbl = 'pjtk2_milestone'
result = get_records(tbl, sqlite)    

for row in result['records']:
    item = Milestone(
        id = row['id'],
        label = row['label'],
        category = row['category'],
        report = row['report'],
        protected = row['protected'],
        order = row['order'],
    )
    item.save()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))


#=========================
#      EMPLOYEE

tbl = 'pjtk2_employee'
result = get_records(tbl, sqlite, True)    

#first fill the employee table
for row in result['records']:
    item = Employee(
        user_id = row['user_id'],
        position = row['position'],
        role = row['role'],
    )
    item.save()

#now update the employee relationships    
for row in result['records']:
    super_id = row['supervisor_id']
    if super_id:
        employee = Employee.objects.get(user_id=row['user_id'])
        employee.supervisor_id = super_id
        employee.save()
   
now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))

   

#=========================
#      PROJECTS

tbl = 'pjtk2_project'
result = get_records(tbl, sqlite)    

for row in result['records']:
    item = Project(
        id = row['id'],
        active = row['active'],
        year = row['year'],
        prj_date0 = row['prj_date0'].split()[0],
        prj_date1 = row['prj_date1'].split()[0],
        prj_cd = row['prj_cd'],
        prj_nm = row['prj_nm'],
        prj_ldr_id = row['prj_ldr_id'],
        comment = row['comment'],
        risk = row['risk'],
        master_database_id = row['master_database_id'],
        project_type_id = row['project_type_id'],
        field_project = row['field_project'],
        owner_id = row['owner_id'],
        dba_id = row['dba_id'],
        funding = row['funding'],
        lake_id = row['lake_id'],
        total_cost = row['total_cost'],
        slug = row['slug'],
    )
    item.save()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))



#=========================
#      PROJECTMILESTONES

tbl = 'pjtk2_projectmilestones'
result = get_records(tbl, sqlite)    

for row in result['records']:

    if row['completed']:
        completed = datetime.datetime.strptime(
            row['completed'],'%Y-%m-%d %H:%M:%S.%f')
        completed = completed.replace(tzinfo=pytz.UTC)
    else:
        completed = None
            
    item = ProjectMilestones(
        project_id = row['project_id'],
        milestone_id = row['milestone_id'],
        required = row['required'],
        completed = completed,
    )
    item.save()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))

#=========================
#      PROJECT REPORTS

tbl = 'pjtk2_report'
result = get_records(tbl, sqlite)    

for row in result['records']:

    if row['uploaded_on']:
        uploaded_on = datetime.datetime.strptime(
            row['uploaded_on'],'%Y-%m-%d %H:%M:%S.%f')
        uploaded_on = uploaded_on.replace(tzinfo=pytz.UTC)
    else:
        uploaded_on = None
            
    item = Report(
        current = row['current'],
        report_path = row['report_path'],
        uploaded_on = row['uploaded_on'],
        uploaded_by_id = row['uploaded_by_id'],
        report_hash = row['report_hash'],
    )
    item.save()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))


#==============================
#   REPORT -to- PROJECT MILESTONE

tbl = 'pjtk2_report_projectreport'
result = get_records(tbl, sqlite)    

#this one's a litte trickier - it'a actually an intermediate table
# between reports and project milestons. That means, we will have to
# use pyscopg to connect to postgres and insert three records outside
# of django's orm.

sql = '''insert into pjtk2_report_projectreport (report_id,
         projectmilestones_id) values (%s, %s)'''

args = ([(x['report_id'], x['projectmilestones_id'])
         for x in result['records']])

pgconn = psycopg2.connect("dbname=pjtk2 user=adam")
pgcur = pgconn.cursor()
pgcur.executemany(sql, args)
pgconn.commit()
pgcur.close()
pgconn.close()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))



#=========================
#      PROJECT FAMILY

tbl = 'pjtk2_family'
result = get_records(tbl, sqlite)    

if len(result['records']) > 0:
    print "** HEY THERE'S FAMILY DATA NOW!!  **"
              
#for row in result['records']:
            
    #item = Report(
#
 #   )
  #  item.save()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))




#=========================
#      PROJECT SISTERS

tbl = 'pjtk2_projectsisters'
result = get_records(tbl, sqlite)    

if len(result['records']) > 0:
    print "** HEY THERE'S SISTER DATA NOW!!  **"
              
#for row in result['records']:
            
    #item = Report(
#
 #   )
  #  item.save()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))



#=========================
#      MESSAGES

tbl = 'pjtk2_message'
result = get_records(tbl, sqlite)    

            
for row in result['records']:
            
    item = Message(
        msg = row['msg'],
        project_milestone_id = row['project_milestone_id'],
        level = row['level'],
    )
    item.save()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))




#=========================
#      MESSAGES-2-USERS

tbl = 'pjtk2_messages2users'
result = get_records(tbl, sqlite)    

           
for row in result['records']:

    if row['created']:
        created = datetime.datetime.strptime(
            row['created'],'%Y-%m-%d %H:%M:%S.%f')
        created = created.replace(tzinfo=pytz.UTC)
    else:
        created = None

    if row['read']:
        read = datetime.datetime.strptime(
            row['read'],'%Y-%m-%d %H:%M:%S.%f')
        read = read.replace(tzinfo=pytz.UTC)
    else:
        read = None    
    
    item = Messages2Users(
        user_id = row['user_id'],
        msg_id = row['msg_id'],
        created = created,
        read = read        
    )
    item.save()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))


#=================================
#  Taggit.tags

tbl = 'taggit_tag'
result = get_records(tbl, sqlite)    

for row in result['records']:
    
    item = Tag(
        name = row['name'],
        slug = row['slug'],        
    )
    item.save()
now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))


#==============================
#   Taggit - TaggedItem

tbl = 'taggit_taggeditem'
result = get_records(tbl, sqlite)    

#this one's a litte trickier - it'a actually an intermediate table
# between tags and tagged items. That means, we will have to
# use pyscopg to connect to postgres and insert three records outside
# of django's orm.

sql = '''insert into taggit_taggeditem (tag_id,
         object_id, content_type_id) values (%s, %s, %s)'''

args = ([(x['tag_id'], x['object_id'], x['content_type_id'])
         for x in result['records']])

pgconn = psycopg2.connect("dbname=pjtk2 user=adam")
pgcur = pgconn.cursor()
pgcur.executemany(sql, args)
pgconn.commit()
pgcur.close()
pgconn.close()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (tbl, now.strftime('%Y-%m-%d %H:%M:%S'))
