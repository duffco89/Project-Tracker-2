'''
=============================================================
c:/1work/Python/djcode/pjtk2/migration/helper_functions.py
Created: 06 Nov 2013 15:30:14


DESCRIPTION:



A. Cottrill
=============================================================
'''

import adodbapi
import datetime
import hashlib
import os
#import pdb
import shutil
import sqlite3
import sys
import re



#===============================================================
# Helper functions:

## def InsertReportRecords(records, reportTable, targdb, fldName= "Report",
##                         commit=False):
##     """A function to insert the records into the report Table in the
##     target (django) database.  The columns in 'records' should
##     correspond to 'Key_PM' and 'Report'.  The functions also resets
##     the forgien keys to associate reports with their orginal project.
##     New primary keys are autmatically assiged to each record.  This
##     funciton create a temporary field to hold the old key, joins on
##     the old key in project master list, updates the forgien key in the
##     report table and then deletes the temporary field.
## 
##     records -
##     reportTable - 
##     targdb -
##     fldName -
##     commit - 
## 
##     """
## 
##     try:
##         sqlcon=sqlite3.connect(targdb)
##         sqlcur=sqlcon.cursor()
## 
##         sql = '''ALTER TABLE %s ADD COLUMN OldKey INT;''' % reportTable
##         sqlcur.execute(sql)
## 
##         #here is the sql to append project tracker data into sqlite:
##         sql = """INSERT INTO %s ("Key_PM_id", "%s", "OldKey")
##             VALUES (?,?,?);""" % (reportTable, fldName)
##         sqlcur.executemany(sql, records)
## 
## 
##         sql = """UPDATE %s SET OldKey=Key_PM_id;""" % reportTable
##         sqlcur.execute(sql)
## 
##         sql = """UPDATE %s SET Key_PM_id = (SELECT id FROM
##                  pjtk2_proj_masterlist WHERE
##                  pjtk2_proj_masterlist.OldKey =
##                  %s.OldKey);""" % (reportTable,reportTable)
##         sqlcur.execute(sql)
## 
## 
## 
##         if commit:
##             sqlcon.commit()
## 
##     except sqlite3.Error, e:
##         if sqlcon:
##             sqlcon.rollback()
## 
##         print "Error %s:" % e.args[0]
## 
## 
##     finally:
##         if sqlcon:
##             sqlcon.close()
## 
## #===============================================================
## 


def msaccess(constr, sql):
    ''''another helper function to submit a sql statement and return
    results from msaccess
    '''
    mdbconn = adodbapi.connect(constr)
    mdbcur = mdbconn.cursor()
    mdbcur.execute(sql)
    result = mdbcur.fetchall()
    mdbcur.close()
    return result


            
def update_db(sql, targdb):
    """
    a simple wrapper that connects to the db and runs the query described by sql
    Arguments:
    - `sql`:
    """
    sqlcon=sqlite3.connect(targdb)
    sqlcur=sqlcon.cursor()
    sqlcur.execute(sql)
    sqlcon.commit()
    sqlcon.close()

            
def get_user_id(username, targdb):
    '''A little helper function that will return the user id number
    given a user name
    '''
    if username != '':
        sqlcon = sqlite3.connect(targdb)
        sqlcur = sqlcon.cursor()
        sql = 'select id from auth_user where username="{0}"'
        sql = sql.format(username)
        sqlcur.execute(sql)
        result = sqlcur.fetchall()
        sqlcon.close()
    try:        
        return result[0][0]
    except IndexError:
        msg = "username '{0}' not found in auth_user"
        msg = msg.format(username)
        print msg
        log = open("./error.log", "a")
        log.write(msg + "\n")
        log.close()                        
        return None

        

            
def get_dbase_id(masterdb, targdb):
    '''A little helper function that will return the id number
    of the master database given it's name'
    '''    
    sqlcon = sqlite3.connect(targdb)
    sqlcur = sqlcon.cursor()
    sql = 'select id from pjtk2_database where master_database="{0}"'
    sql = sql.format(masterdb)
    sqlcur.execute(sql)
    result = sqlcur.fetchall()
    sqlcon.close()
    #return result[0][0]
    try:
        return result[0][0]
    except IndexError:
        msg = "master database '{0}' not found in pjtk2_database"
        msg = msg.format(masterdb)
        print msg
        log = open("./error.log", "a")
        log.write(msg + "\n")
        log.close()                        
        return None
        

    
def get_projtype_id(projtype, targdb):
    '''A little helper function that will return the id number
    of the project type given it's name'
    '''   
    sqlcon = sqlite3.connect(targdb)
    sqlcur = sqlcon.cursor()
    sql = 'select id from pjtk2_projecttype where project_type="{0}"'
    sql = sql.format(projtype)
    sqlcur.execute(sql)
    result = sqlcur.fetchall()
    sqlcon.close()
    #return result[0][0]
    try:
        return result[0][0]
    except IndexError:
        msg = "project_type '{0}' not found in pjtk2_projecttype"
        msg = msg.format(projtype)
        print msg
        log = open("./error.log", "a")
        log.write(msg + "\n")
        log.close()                        
        return None
         

def get_project_code(project_id, targdb):
    '''A little helper function that will return the project code 
    for a project given its id
    '''   
    sqlcon = sqlite3.connect(targdb)
    sqlcur = sqlcon.cursor()
    sql = 'select prj_cd from pjtk2_project where id={0}'
    sql = sql.format(project_id)
    sqlcur.execute(sql)
    result = sqlcur.fetchall()
    sqlcon.close()
    #return result[0][0]
    try:
        return result[0][0]
    except IndexError:
        msg = "project with id='{0}' not found in pjtk2_project"
        msg = msg.format(project_id)
        print msg
        log = open("./error.log", "a")
        log.write(msg + "\n")
        log.close()                        
        return None

        

def get_project_id(OldKey, targdb):
    '''A little helper function that will return the id number
    of the project given it's old primary key'
    '''   
    sqlcon = sqlite3.connect(targdb)
    sqlcur = sqlcon.cursor()
    sql = 'select id from pjtk2_project where OldKey={0}'
    sql = sql.format(OldKey)
    sqlcur.execute(sql)
    result = sqlcur.fetchall()
    sqlcon.close()
    #return result[0][0]
    try:
        return result[0][0]
    except IndexError:
        msg = "project with oldKey='{0}' not found in pjtk2_project"
        msg = msg.format(OldKey)
        print msg
        log = open("./error.log", "a")
        log.write(msg + "\n")
        log.close()                
        return None
    

def get_milestone_id(label, targdb):
    '''A little helper function that will return the id number
    of the milestone given it's label'
    '''   
    sqlcon = sqlite3.connect(targdb)
    sqlcur = sqlcon.cursor()
    sql = 'select id from pjtk2_milestone where label="{0}"'
    sql = sql.format(label)
    sqlcur.execute(sql)
    result = sqlcur.fetchall()
    sqlcon.close()
    try:
        return result[0][0]
    except IndexError:
        msg = "label '{0}' not found in pjtk2_milestone".format(label)
        print msg
        log = open("./error.log", "a")
        log.write(msg + "\n")
        log.close()        
        return None
    


def get_project_milestone_id(project_id, milestone_id, targdb):
    '''A little helper function that will return the id number
    of the project_milestone given it's label'
    '''   
    sqlcon = sqlite3.connect(targdb)
    sqlcur = sqlcon.cursor()
    sql = '''select id from pjtk2_projectmilestones
             where project_id={0} and milestone_id={1}'''
    sql = sql.format(project_id, milestone_id)
    sqlcur.execute(sql)
    result = sqlcur.fetchall()
    sqlcon.close()
    try:
        return result[0][0]
    except IndexError:
        msg = ("project_milestone with project_id ='{0}' and milestone_id"
               " = {1} not found").format(project_id, milestone_id)        
        print msg
        log = open("./error.log", "a")
        log.write(msg + "\n")
        log.close()        
        return None
    

def move_report_file(src_path, dest):
    '''a helper function used by migrate_reports() to actually move
    the report file from the source to the media path.  dest should
    already include the complete media_path and have all spaces
    replaced by underscores.  If there is problem moving the file, an
    entry will be created in ~/errors.log
    '''

    try:
        shutil.copyfile(src_path, dest)
        return 0
    except IOError:
        print "Warning - unable to copy {0}".format(src_path)
        log = open("./error.log", "a")
        log.write(src_path + "\n")
        log.close()
        return 1

        

def migrate_reports(oldKey, src_path, milestone_id, user_id,
                    media_url, media_path, targdb):
    '''This function moves a file from the old directory(src_path)
    into the media_url for the django application, inserts the
    appropriate records in [pjtk2_reports],
    [pjtk2_report_projectreports], and updates
    [pjtk2_projectmilestones].[completed_on] field to associate this
    report with a particular project and flag that it has been
    completed.
    

    oldKey - primary key associated with this report in ms access
    version of project tracker.  It is used to get new project id from
    the django back-end
    
    src_path - the full path to the report we're going to copy
    
    milestone_id - what milestone is this report associated with
    
    user_id - your user_id in the django app (required foriegn key in
       reports table)

    media_url - the url from which django will serve reports
    
    media_path - full path to the media/report directory of the django app
    
    targdb - path to database were records will be inserted

    '''


    #copy the file from the server to MEDIA_PATH
    fname = os.path.split(src_path)[-1]
    #remove any spaces from filen name to make it easier to serve:
    fname = fname.strip().replace(" ","_")
    dest = os.path.join(media_path, fname)
    #print dest

    move_report_file(src_path, dest)
        
    project_id = get_project_id(oldKey, targdb)
    now = datetime.datetime.utcnow()
        
    #quit if either project_id or project_milestone_id are None
    if project_id is None:
        return None
    else:                                                        
        project_milestone_id = get_project_milestone_id(project_id,
                                                        milestone_id, targdb) 
    if project_milestone_id is None:
        return None

    else:
        #insert a record into pjtk2_report
        args = dict(
            current = 1,
            report_path = os.path.join(media_url, fname).replace("\\", "/"),
            uploaded_on = now,
            uploaded_by_id = str(user_id),            
            report_hash = hashlib.sha1(dest).hexdigest(),
        )

        try:
            sqlcon=sqlite3.connect(targdb)
            sqlcur=sqlcon.cursor()

            sql = "INSERT INTO pjtk2_report({0}) values ({1})".format(
                ", ".join(args.keys()),
                ", ".join('?' * len(args.keys())))

            sqlcur.execute(sql,args.values())
            #get the id of the report we just inserted:
            report_id = sqlcur.lastrowid            

            #add a record to pjtk2_report_milestone
            sql = """INSERT INTO pjtk2_report_projectreport(report_id,
                     projectmilestones_id) values (?,?)"""
            sqlcur.execute(sql,(report_id, project_milestone_id))

            sql = """UPDATE pjtk2_projectmilestones set completed=?
                     where id=?"""
            sqlcur.execute(sql,(now, project_milestone_id))
            sqlcon.commit()
        except sqlite3.error, e:
            sqlcon.rollback()                
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            sqlcon.close()

        return None


def drop_report_tables(targdb):
    '''** CAREFUL ** - a helper function used to clear out the tables
    associated with project reports.  No warning is issued, the tables
    are just dropped.
    '''
    sqlcon = sqlite3.connect(targdb)
    sqlcur = sqlcon.cursor()
    sql = '''Drop table pjtk2_projectmilestones'''
    sqlcur.execute(sql)
    sql = '''Drop table pjtk2_report_projectreport'''
    sqlcur.execute(sql)
    sql = '''Drop table pjtk2_report'''
    sqlcur.execute(sql)
    
    sqlcon.commit()
    sqlcon.close()

    print "Report tables successfully dropped."


def clear_upload_dir(media_path):
    '''another helper function to make development easier this
    functional remaove all files from media root.

    '''
    for the_file in os.listdir(media_path):
        file_path = os.path.join(media_path, the_file)
        try:
            os.unlink(file_path)
        except Exception, e:
            print e