# this was my first attemp - trying to simpley dump from sqlite to sql,
# process the sql and then import in postgres - no love

##  import re
##  import os
##  
##  curdir = "c:/1work/Python/djcode/pjtk2/migration/"
##  f1name = os.path.join(curdir, 'sqlite_data.sql')
##  f2name = os.path.join(curdir, 'sqlite_data.sql.tmp')
##  
##  f1 = open(f1name, 'r')
##  f2 = open(f2name, 'w')
##  for line in f1:
##      line = line.replace('PRAGMA', '')
##      line = line.replace('sqlite_sequence','')
##      line = line.replace('integer PRIMARY KEY AUTOINCREMENT',
##                          'serial PRIMARY KEY')
##      line = line.replace('datetime','timestamp')
##  
##      line = re.sub('integer[(][^)]*[)]', 'integer', line)
##      line = re.sub('text[(]\([^)]*\)[)]', 'varchar(\1)', line)
##      
##      f2.write(line)
##  f1.close()
##  f2.close()
##  
##  print "Done!!"
##  

#===================================================================
##  2nd Try!
#   here I thought I would use db_api to query sqlite them import
#   directly to pg - no luck, the lack of boolean fileds in sqlite
#   make this approach complicated and fragile
##  
##  import os
##  import sqlite3
##  import psycopg2
##  from datetime import datetime
##  
##  #here is the database we want to append into
##  
##  sqlite = "C:/1work/Python/djcode/pjtk2/db/pjtk2.db"
##  
##  
##  #=======================
##  #        USERS
##  
##  tbl = 'auth_user'
##  sqlcon=sqlite3.connect(sqlite)
##  sqlcur=sqlcon.cursor()
##  sql = "SELECT * FROM {0} where username <> 'adam'".format(tbl)
##  sqlcur.execute(sql)
##  flds = list(map(lambda x: x[0], sqlcur.description))
##  result = sqlcur.fetchall()
##  sqlcon.close()
##  
##  sql = """insert into {0} ({1}) values ({2})"""
##  sql = sql.format(tbl, ", ".join(flds),
##                   ",".join(["%s"] * len(flds)))
##  
##  
##  #Insert the data into postgres
##  pgconn = psycopg2.connect("dbname=pjtk2 user=adam")
##  pgcur = pgconn.cursor()
##  pgcur.executemany(sql, result)
##  pgcur.close()
##  pgconn.close()
##  
##  
##  print "Done migrating Users ({0})".format(datetime.now())



#===================================================================
##  3nd Try!
## this attemp will use sqlachemy to move data into post gres.

import os
import sqlite3
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy.base import WKTSpatialElement


from sqa_models import *

#here is the database we want to get the data out of:
sqlite = "C:/1work/Python/djcode/pjtk2/db/pjtk2.db"


#create a sqlachemy engine and session we can use to connect to postgres
#engine = create_engine('postgresql://adam:pjtke@localhost/pjtk2')
#Session = sessionmaker(bind=engine)
#session = Session()


#=======================
#        USERS
# STOP - load users with ./get_django_users.py


#=======================

tbl = 'pjtk2_database'
sqlcon=sqlite3.connect(sqlite)
sqlcon.row_factory = sqlite3.Row
sqlcur=sqlcon.cursor()
sql = "SELECT * FROM {0}".format(tbl)
sqlcur.execute(sql)
flds = list(map(lambda x: x[0], sqlcur.description))
result = sqlcur.fetchall()
sqlcon.close()

print "Fields in {0}:".format(tbl)
for fld in flds:
    print "\t{0}".format(fld)
    
jj = result[0]
kk = Database(
        master_database = jj['master_database'],
        path = jj['path']
    )
    

    
for row in result:
    item = Database(
        master_database = row['master_database'],
        path = row['path']
    )
    #session.add(item)

session.commit()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))



