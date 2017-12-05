'''=============================================================
c:/1work/Python/djcode/pjtk2/migration/get_spatial_data.py
Created: 13 Nov 2013 16:19:39

DESCRIPTION:

This script compiles all of the spatial data from each of our master
datasets and imports it into project tracker (pjtk2).  For most
projects, actual nets set locations are returned.  For some projects
where large numbers of samples occured at the same location, a single
lat-lon is returned and sample number is not retained (e.g. - creels
and derby sampling).

Database not currently included in this scripts:
- Sturgeon Master
- Lake whitefish movement study
- CWT cooperative collections
- cormorant work (where is that data any how?)
- other projects and programs I don't know about

To refresh the spatial data in pjtk2 simply run:
python get_spatial_data.py

Orphans.csv and Omissions.csv are created by this script and
include lists of projects in project tracker that should have
data but are not in any of our master databases and a second list of
projects that are in our master databases but are not yet in tracker.

Finally, this script also contains a chunk of code that updates the
milestones for projects.  If a project has spatial data, it is assumed
that it was approved, conducted, scrubbed, aged and merged. If the
proejct was run prior to 2012, it is also assumed to have been signed
off. *** NOTE - This is only a work around - while we transition from
ms access to django.  Once we go live, this chunk of code should be
removed. ***


A. Cottrill
=============================================================

'''


import csv
import os
import psycopg2
import pyodbc

PG_USER = 'adam'
PG_DB = 'pjtk2'

PG_HOST = '***REMOVED***'
#PG_HOST = '127.0.0.1'

OUTDIR = 'C:/1work/scrapbook/project_tracker'

MASTERS = {
    'offshore': {
        'path': 'Z:/Data Warehouse/Assessment/Index/Offshore/IA_OFFSHORE.mdb',
        'table': 'Offshore_FN121',
        'sam': 'SAM',
        'ddlat': 'dd_lat',
        'ddlon': 'dd_lon',
        'groupby': False,
     },

    'nearshore': {
        'path': 'Z:/Data Warehouse/Assessment/Index/Nearshore/IA_NEARSHORE.mdb',
        'table': 'IA121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'groupby': False,
     },


    'smallfish': {
        'path': ('Z:/Data Warehouse/Assessment/Index/Nearshore/' +
                 'Small_Fish/COA_Nearshore_Smallfish.mdb'),
        'table': '121',
        'sam': 'SAM',
        'ddlat': 'dd_lat',
        'ddlon': 'dd_lon',
        'groupby': False,
     },

    'fishway': {
        'path': 'Z:\Data Warehouse\Assessment\Fishway\Fishway_Master.mdb',
        'table': 'IM_121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'groupby': True,
     },

     'sturgeon': {
         #'path':('Z:/Data Warehouse/Derived Datasets/UNIT PROJECTS/' +
         #        'Sturgeon/Sturgeon Master.mdb'),

         #'path': ('Z:/Data Warehouse/Derived Datasets/UNIT PROJECTS/Sturgeon/' +
         #         'SturgeonMasterpriortoLCMupdate01APR2011/Sturgeon Master.mdb'),

         'path': ('Z:/Data Warehouse/Assessment/Index/Sturgeon/' +
                  'SturgeonMaster.mdb'),
          'table': 'Sturgeon_FN121',
         'sam': 'SAM',
         'ddlat': 'dd_lat',
         'ddlon': 'dd_lon',
        'groupby': False,
      },


    'comcatch': {
        'path':('Z:/Data Warehouse/Commercial Fisheries/Catch Sampling/' +
                'CF_Master.mdb'),
        'table': 'Final_FN121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'groupby': False,
     },


    'stocking': {
        'path':('Y:/Information Resources/Dataset_Utilities/FS_Maker/' +
                'FS_Master.mdb'),
        'table': 'FS_Events',
        'sam':  'EVENT',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'groupby': False,
     },

    'creel': {
        'path':('Z:/Data Warehouse/Recreational Fisheries/Creel/SC/' +
                'SC_Master.mdb'),
        'table': 'FINAL_FN121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
        'groupby': True,
     },


    'sportfish':{
        'path':('Z:/Data Warehouse/Recreational Fisheries/Angler Diary/Sf/' +
                'SF_MASTER.mdb'),
        'table': 'FN121',
        'sam': 'SAM',
        'ddlat': 'DD_LAT',
        'ddlon': 'DD_LON',
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
        'groupby': False,
     },
}


def build_sql(table, sam, dd_lat, dd_lon, groupby=True):

    if groupby:

        sql_base = '''SELECT DISTINCT [PRJ_CD], [{1}], [{2}] FROM [{0}]
        WHERE (((PRJ_CD) Is Not Null)  AND (([{1}]) Is Not Null)
        AND (([{2}]) Is Not Null));'''
        #tablename, dd_lat, dd_lon
        sql = sql_base.format(table, dd_lat, dd_lon)
        return sql

    else:
        sql_base = '''SELECT [PRJ_CD], [{1}], [{2}], [{3}] FROM [{0}]
           WHERE (((PRJ_CD) Is Not Null) AND (([{1}]) Is Not Null) AND
        (([{2}]) Is Not Null) AND (([{3}]) Is Not Null));'''
        #tablename, sam, dd_lat, dd_lon
        sql = sql_base.format(table, sam, dd_lat, dd_lon)
        return sql



#clean up benthic master
#NOTE - add projects for CWT fiasco
# fix fsmaster  - add 'sam'' to functios



#=============================================
#  DO IT

samplepoints = []

for db in MASTERS.keys():

    dbase = MASTERS[db]

    constr = r"DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={0}"
    constr = constr.format(dbase['path'])

    mdbconn = pyodbc.connect(constr)
    mdbcur = mdbconn.cursor()


    # create a cursor
    #try the lookup tables first - keep things simple
    mdbcur = mdbconn.cursor()

    sql = build_sql(dbase['table'], dbase['sam'], dbase['ddlat'],
                    dbase['ddlon'], dbase['groupby'])
    mdbcur.execute(sql)
    result = mdbcur.fetchall()
    print("There were {0} records found in {1}".format(len(result),
                                                       db))

    mdbconn.close()

    if dbase['groupby']:
        for row in result:
            #repeat project code if sam not available
            samplepoints.append((db, row[0], row[0], row[1], row[2]))
    else:
        for row in result:
            samplepoints.append((db, row[0], row[1], row[2], row[3]))




#==================================
#    INSERT SPATIAL DATA

#constr = "dbname={0} user={1}".format(PG_DB, PG_USER)
constr = "host={0} dbname={1} user={2} password='django'".format(PG_HOST, PG_DB, PG_USER)
pgconn = psycopg2.connect(constr)
pgcur = pgconn.cursor()

print('Making temporary spatial table...')

sql = """DROP TABLE IF EXISTS spatial_tmp"""
pgcur.execute(sql)

sql = """CREATE TABLE spatial_tmp
(
  id serial NOT NULL,
  prj_cd character(13) NOT NULL,
  dbase character varying(30),
  sam character varying(30),
  geom geometry(Point,4326) NOT NULL
)
"""
pgcur.execute(sql)
pgconn.commit()
print('Inserting points into temporary spatial table...')

args = ([{'dbase': x[0], 'prj_cd':x[1], 'sam':x[2], 'ddlat':x[3], 'ddlon':x[4]}
         for x in samplepoints])

sql = """INSERT INTO spatial_tmp (dbase, prj_cd, sam, geom)
         VALUES(%(dbase)s, %(prj_cd)s, %(sam)s,
         ST_SetSRID(ST_MakePoint(%(ddlon)s, %(ddlat)s), 4326));"""

pgcur.executemany(sql, args)
pgconn.commit()

#===================
#check for data missing from MASTERS and data in MASTERS without project here
print('continue...')

#here are the projects that still have spatial data but can't be found
#in project list

sql = """SELECT DISTINCT CASE
         WHEN CAST(SUBSTRING(sp.prj_cd,7,2) AS int) < 50
         THEN '20' ||SUBSTRING(sp.prj_cd,7,2)
         ELSE '19' ||SUBSTRING (sp.prj_cd,7,2)
       END AS year,
       sp.dbase,
       sp.prj_cd
FROM spatial_tmp sp
WHERE UPPER(sp.prj_cd) NOT IN (
SELECT DISTINCT UPPER(p.prj_cd) AS foo FROM pjtk2_project p)
ORDER BY dbase,
         prj_cd;"""

pgcur.execute(sql)
orphans = pgcur.fetchall()

fname = os.path.join(OUTDIR,'orphans.csv')
with open(fname, 'w', newline='') as f:
    writer = csv.writer(f, lineterminator=os.linesep)
    writer.writerow([x[0] for x in pgcur.description])
    writer.writerows(orphans)
print("Done writing orphans.csv")


#these are projects that have a completion product of some kind but do
#not appear in the master databases anywhere

sql = """
-- approved, active, field projects in project tracker that do not have spatial
-- data associated with them
SELECT DISTINCT p.year,
       p.prj_cd,
       p.prj_nm,
       u.first_name || ' ' || u.last_name AS project_lead,
       prjtype.field_component
FROM pjtk2_project p
  JOIN auth_user AS u ON u.id = p.prj_ldr_id
  JOIN pjtk2_projecttype AS prjtype ON prjtype.id = p.project_type_id
  JOIN pjtk2_projectmilestones pms ON p.id = pms.project_id
  JOIN pjtk2_milestone ms ON ms.id = pms.milestone_id
WHERE
ms.label = 'Field Work Conducted'
AND   field_component IS TRUE
AND   p.active IS TRUE
AND   p.cancelled IS FALSE
--and pms.completed is not null
AND   UPPER(p.prj_cd) NOT IN (
-- projects with spatial data
SELECT DISTINCT UPPER(prj_cd) as PRJ_CD FROM spatial_tmp)
ORDER BY p.year DESC;

"""

pgcur.execute(sql)
omissions = pgcur.fetchall()

fname = os.path.join(OUTDIR,'omissions.csv')
with open(fname, 'w', newline='') as f:
    writer = csv.writer(f, lineterminator=os.linesep)
    writer.writerow([x[0] for x in pgcur.description])
    writer.writerows(omissions)
print("Done writing omissions.csv")

#=========================
###Update milestones
### ** NOTE ** this is a work around - delete this section once project tracker goes live!
###if there is spatial data, the project must have been completed
###update all of the milestones for all of the projects in spatial.
##
##sql = """ UPDATE pjtk2_projectmilestones pms2
##          SET completed = NOW()
##          WHERE pms2.id IN (
##          SELECT distinct pms.id
##                  FROM pjtk2_projectmilestones pms
##                    JOIN pjtk2_project p ON pms.project_id = p.id
##                    JOIN pjtk2_milestone ms ON ms.id = pms.milestone_id
##                    JOIN spatial_tmp AS sp ON sp.prj_cd = p.prj_cd
##                  WHERE pms.completed is NULL
##                  AND   p.year::int4 < 2012
##                  AND   ms.report = FALSE);"""
##pgcur.execute(sql)
### we don't want to sign off on recent projects though - rest the
### signoff project milestone for those projects
##
##sql = """UPDATE pjtk2_projectmilestones pms2
##           SET completed = NULL
##           WHERE pms2.id IN (
##           SELECT distinct pms.id
##                  FROM pjtk2_projectmilestones pms
##                    JOIN pjtk2_project p ON pms.project_id = p.id
##                    JOIN pjtk2_milestone ms ON ms.id = pms.milestone_id
##                    JOIN spatial_tmp AS sp ON sp.prj_cd = p.prj_cd
##                  WHERE pms.completed is not NULL
##                  AND   p.year::int4 >= 2012
##                  AND ms.label = 'Sign off');"""
##pgcur.execute(sql)
##
##
# Finally update the spatial data:

#clear out the old data
sql = """DELETE FROM pjtk2_samplepoint"""
pgcur.execute(sql)
print('Updating spatial data...')
#now update pjtk2_samplepoint by joining on project code (don't have
# to worry about projects without spatial data or projects not in
# tracker (yet))
sql = """insert into pjtk2_samplepoint (project_id, sam, geom)
         select pjtk2_project.id as project_id, sam, geom from spatial_tmp
         join pjtk2_project on pjtk2_project.prj_cd=spatial_tmp.prj_cd"""
pgcur.execute(sql)

#cleanup
print('Cleaning up...')
sql = """DROP TABLE spatial_tmp"""
pgcur.execute(sql)
pgconn.commit()

pgcur.close()
pgconn.close()

print('Done uploading spatial data!!')
