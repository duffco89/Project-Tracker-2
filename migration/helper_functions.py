'''
=============================================================
c:/1work/Python/djcode/pjtk2/migration/helper_functions.py
Created: 06 Nov 2013 15:30:14


DESCRIPTION:



A. Cottrill
=============================================================
'''



#===============================================================
# Helper functions:

def InsertReportRecords(records, reportTable, targdb, fldName= "Report",
                        commit=False):
    """
    A function to insert the records into the reportTable in the target
    database.  The columns in 'records' should correspond to 'Key_PM'
    and 'Report'.  The functions also resets the forgien
    keys to associate reports with their orginal project.  New primary
    keys are autmatically assiged to each record.  This funciton create
    a temporary field to hold the old key, joins on the old key in
    project master list, updates the forgien key in the report table
    and then deletes the temporary field.
    """

    try:
        sqlcon=sqlite3.connect(targdb)
        sqlcur=sqlcon.cursor()

        sql = '''ALTER TABLE %s ADD COLUMN OldKey INT;''' % reportTable
        sqlcur.execute(sql)

        #here is the sql to append project tracker data into sqlite:
        sql = """INSERT INTO %s ("Key_PM_id", "%s", "OldKey")
            VALUES (?,?,?);""" % (reportTable, fldName)
        sqlcur.executemany(sql, records)


        sql = """UPDATE %s SET OldKey=Key_PM_id;""" % reportTable
        sqlcur.execute(sql)

        sql = """UPDATE %s SET Key_PM_id = (SELECT id FROM
                 pjtk2_proj_masterlist WHERE
                 pjtk2_proj_masterlist.OldKey =
                 %s.OldKey);""" % (reportTable,reportTable)
        sqlcur.execute(sql)



        if commit:
            sqlcon.commit()

    except sqlite3.Error, e:
        if sqlcon:
            sqlcon.rollback()

        print "Error %s:" % e.args[0]


    finally:
        if sqlcon:
            sqlcon.close()

#===============================================================

def update_db(sql):
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

            
def get_user_id(username):
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
        return result[0][0]
    else:
        return None
           

            
def get_dbase_id(masterdb):
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
    return result[0][0]

    
def get_projtype_id(projtype):
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
    return result[0][0]
    #return (projtype, result)
