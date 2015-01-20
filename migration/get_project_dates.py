'''=============================================================
c:/1work/Python/djcode/pjtk2/migration/get_project_dates.py
Created: 14 Jan 2015 15:43:57


DESCRIPTION:

This script was developed from get_spatial_data.py (and should be
merged with it to faciliate annual/frequent updates).

This scripts gets the start and end date for every project in the
master databases and then updates prj_date0 and prj_date1 in project
tracker.  This script should be run each time a project is merged into
a master set.  Project start and end dates are required fields when a
project is created, but can't be known until the project is complete.
This script ensures that project tracker reflects what is in the
databases.

A. Cottrill
=============================================================

'''

import csv
import pyodbc
import datetime
from dateutil import parser
import psycopg2

PG_USER = 'adam'
PG_DB = 'pjtk2'

PG_HOST = '142.143.160.56'
#PG_HOST = '127.0.0.1'


masters = {
    'offshore': {
        'path': 'Z:/Data Warehouse/Assessment/Index/Offshore/IA_OFFSHORE.mdb',
        'table': 'Offshore_FN121',
        'sam': 'SAM',
        'ddlat': 'dd_lat',
        'ddlon': 'dd_lon',
        'effdt0': 'effdt0',
        'effdt1': 'effdt1',
        'groupby': False,
     },

    'nearshore': {
        'path': 'Z:/Data Warehouse/Assessment/Index/Nearshore/IA_NEARSHORE.mdb',
        'table': 'IA121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'effdt0': 'effdt0',
        'effdt1': 'effdt1',
        'groupby': False,
     },


    'smallfish': {
        'path': ('Z:/Data Warehouse/Assessment/Index/Nearshore/' +
                 'Small_Fish/COA_Nearshore_Smallfish.mdb'),
        'table': '121',
        'sam': 'SAM',
        'ddlat': 'dd_lat',
        'ddlon': 'dd_lon',
        'effdt0': 'effdt0',
        'effdt1': 'effdt1',
        'groupby': False,
     },

    'fishway': {
        'path': 'Z:\Data Warehouse\Assessment\Fishway\Fishway_Master.mdb',
        'table': 'IM_121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'effdt0': 'effdt0',
        'effdt1': 'effdt1',
        'groupby': True,
     },


     'sturgeon': {

         'path': ('Z:/Data Warehouse/Assessment/Index/Sturgeon/' +
                  'SturgeonMaster.mdb'),
         'table': 'Sturgeon_FN121',
         'sam': 'SAM',
         'ddlat': 'dd_lat',
         'ddlon': 'dd_lon',
        'effdt0': 'effdt0',
        'effdt1': 'effdt1',
        'groupby': False,
      },




    'comcatch': {
        'path':('Z:/Data Warehouse/Commercial Fisheries/Catch Sampling/' +
                'CF_Master.mdb'),
        'table': 'Final_FN121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'effdt0': 'DATE',
        'effdt1': 'DATE',
        'groupby': False,
     },


    'stocking': {
        'path':('Y:/Information Resources/Dataset_Utilities/FS_Maker/' +
                'FS_Master.mdb'),
        'table': 'FS_Events',
        'sam':  'EVENT',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'effdt0': 'Event_Date',
        'effdt1': 'Event_Date',
        'groupby': False,
     },

    'creel': {
        'path':('Z:/Data Warehouse/Recreational Fisheries/Creel/SC/' +
                'SC_Master.mdb'),
        'table': 'FINAL_FN121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'effdt0': 'EFFDT0',
        'effdt1': 'EFFDT0',
        'groupby': True,
     },


    'sportfish':{
        'path':('Z:/Data Warehouse/Recreational Fisheries/Angler Diary/Sf/' +
                'SF_MASTER.mdb'),
        'table': 'FN121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'effdt0': 'EFFDT0',
        'effdt1': 'EFFDT0',
        'groupby': True,
     },


    'benthic': {
        'path':('Z:/Data Warehouse/Derived Datasets/UNIT PROJECTS/Benthics/' +
                 'Lake Huron Benthics.mdb'),
        #'path':'Y:/File Transfer/Lake Huron Benthics.mdb',
        'table': 'LH_benthics',
        'sam': 'Station ID',
        'ddlat': 'DD Latitude',
        'ddlon': 'DD Longitude',
        'effdt0': 'Date',
        'effdt1': 'Date',
        'groupby': False,
     },
}


def build_sql2(db_dict):
    '''a little helper function that will build the sql statement to get
    the start and end data of each project in the table (database)'''

    sql_base="""SELECT PRJ_CD, Min([{effdt0}]) AS PRJ_Start, Max([{effdt1}])
    AS PRJ_END
    FROM [{table}]
    GROUP BY PRJ_CD;"""
    sql = sql_base.format(**db_dict)
    return sql


prj_dates = []

#loop over our database dictionary and query each one for the project info.
for db in masters.keys():

    dbase = masters[db]

    constr = r"DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={0}"
    constr = constr.format(dbase['path'])

    mdbconn = pyodbc.connect(constr)
    mdbcur = mdbconn.cursor()

    # create a cursor
    #try the lookup tables first - keep things simple
    mdbcur = mdbconn.cursor()
    sql = build_sql2(dbase)
    try:
        mdbcur.execute(sql)
        result = mdbcur.fetchall()
        print("There were {0} records found in {1}".format(len(result),
                                                       db))
    except:
        print('Problem with {}'.format(db))

    mdbconn.close()

    for row in result:
        prj_dates.append([row[0], row[1], row[2]])


#convert the list of tuples returned by the db to a list of lists
prj_list = [[x[0], x[1], x[2]] for x in prj_dates]

#now covert each of dates  to datetime objects (if they aren't already') and
#capture any that can't be converted
bad_start = []
bad_end = []
for prj in prj_list:
    if prj[1] and prj[1].__class__ != datetime.datetime:
        try:
            prj[1] = parser.parse(prj[1])
        except TypeError:
            bad_start.append(prj)
    if prj[2] and prj[2].__class__ != datetime.datetime:
        try:
            prj[2] = parser.parse(prj[2])
        except TypeError:
            bad_end.append(prj)

print("There were {} bad start dates found.".format(len(bad_start)))
print("There were {} bad end dates found.".format(len(bad_end)))

#now write prj_dates into a temporary table in project tracker
#and compare project start and end dates
# update those where they are different.

constr = "host={0} dbname={1} user={2}".format(PG_HOST, PG_DB, PG_USER)
pgconn = psycopg2.connect(constr)
pgcur = pgconn.cursor()

print('Making temporary project dates table...')

sql = """DROP TABLE IF EXISTS prj_dates_tmp"""
pgcur.execute(sql)

sql = """CREATE TABLE prj_dates_tmp
(
  id serial NOT NULL,
  prj_cd character(13) NOT NULL,
  prj_start DATE,
  prj_end DATE
)
"""
pgcur.execute(sql)
pgconn.commit()
print('Inserting project dates into temporary table...')

args = ([{'prj_cd': x[0], 'prj_start':x[1], 'prj_end':x[2]}
         for x in prj_list])

sql = """INSERT INTO prj_dates_tmp (prj_cd, prj_start, prj_end)
         VALUES(%(prj_cd)s, %(prj_start)s, %(prj_end)s);"""

pgcur.executemany(sql, args)
pgconn.commit()

#=============================================================
#write out some basic information about project that have start
# dates different than the master:

sql = """-- start dates that differ
SELECT master_database as dbase, prj.year,
       dates.prj_cd,
       prj_start AS master_start,
       prj_date0 AS tracker_start,
       prj_start - prj_date0 AS diff
FROM prj_dates_tmp dates
  JOIN pjtk2_project prj ON prj.prj_cd = dates.prj_cd
  join pjtk2_database db on db.id=prj.master_database_id
WHERE prj.prj_date0 != dates.prj_start
--and db.master_database = 'Fish Stocking'
ORDER BY dbase,
       prj.year DESC,
       prj.prj_cd;"""

pgcur.execute(sql)
rs = pgcur.fetchall()
fname = 'c:/1work/Python/djcode/pjtk2/migration/start_dates.csv'
with open(fname, 'w') as f:
    writer = csv.writer(f)
    writer.writerow([x[0] for x in pgcur.description])
    writer.writerows(rs)

#=============================================================
#write out some basic information about project that have ends
#different than the master:

sql = """-- end dates that differ
SELECT master_database as dbase, prj.year,
prj.year,
       dates.prj_cd,
       prj_end AS master_end,
       prj_date1 AS tracker_end,
       prj_end - prj_date1 AS diff
FROM prj_dates_tmp dates
  JOIN pjtk2_project prj ON prj.prj_cd = dates.prj_cd
 join pjtk2_database db on db.id=prj.master_database_id
WHERE prj.prj_date1 != dates.prj_end
--and db.master_database = 'Fish Stocking'
ORDER BY dbase,
prj.year DESC,
         prj.prj_cd;"""

pgcur.execute(sql)
rs = pgcur.fetchall()
fname = 'c:/1work/Python/djcode/pjtk2/migration/end_dates.csv'
with open(fname, 'w') as f:
    writer = csv.writer(f)
    writer.writerow([x[0] for x in pgcur.description])
    writer.writerows(rs)

#=============================================================
# update project tracker:

print('Updating START dates....')
sql = """-- update the project start dates from the masters:
UPDATE pjtk2_project
   SET prj_date0 = prj_start
FROM prj_dates_tmp
WHERE prj_dates_tmp.prj_cd = pjtk2_project.prj_cd
and prj_date0 != prj_start;"""
pgcur.execute(sql)

print('Updating END dates....')
sql = """-- update the project End dates from the masters:
UPDATE pjtk2_project
   SET prj_date1 = prj_end
FROM prj_dates_tmp
WHERE prj_dates_tmp.prj_cd = pjtk2_project.prj_cd
and prj_date1 != prj_end;"""
pgcur.execute(sql)

print('Cleaning up...')
sql = """DROP TABLE prj_dates_tmp"""
pgcur.execute(sql)
pgconn.commit()

pgcur.close()
pgconn.close()

print('Done updating project dates!!')
