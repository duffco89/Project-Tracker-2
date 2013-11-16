'''
=============================================================
c:/1work/Python/djcode/pjtk2/migration/get_spatial_data.py
Created: 13 Nov 2013 16:19:39


DESCRIPTION:

This script complies all of the spatial data from each of our master
datasets and imports it into project tracker (pjtk2).  For most
projects, actual nets set lcoations are returned.  For some projects
where large numbers of samples occure at the same location, a single
lat-lon is returned and sample number is not retains.

Database not currently included in this scripts:
- Sturgeon Master
- Lake whitefish movement study
- CWT cooperative collections
- other projects and programs I don't know about

To refresh the spatial data in pjtk2 simply run:
python get_spatial_data.py


A. Cottrill
=============================================================
'''


import adodbapi
import psycopg2

PG_USER = 'adam'
PG_DB = 'pjtk2'

masters = {
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
                     
    ## 'sturgeon': {
    ##     #'path':('Z:/Data Warehouse/Derived Datasets/UNIT PROJECTS/' +
    ##     #        'Sturgeon/Sturgeon Master.mdb'),
    ## 
    ##     'path': ('Z:/Data Warehouse/Derived Datasets/UNIT PROJECTS/Sturgeon/' +
    ##              'SturgeonMasterpriortoLCMupdate01APR2011/Sturgeon Master.mdb'),
    ##     'table': 'Sturgeon_FN121',
    ##     'sam': 'SAM',                
    ##     'ddlat': 'dd_lat',
    ##     'ddlon': 'dd_lon',     
    ##  },

                 
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
        'table': 'FN121_MASTER',
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
    
for db in masters.keys():

    dbase = masters[db]

    constr = 'Provider=Microsoft.Jet.OLEDB.4.0; Data Source={0}'
    constr = constr.format(dbase['path'])

    mdbconn = adodbapi.connect(constr)
    # create a cursor
    #try the lookup tables first - keep things simple
    mdbcur = mdbconn.cursor()

    sql = build_sql(dbase['table'], dbase['sam'], dbase['ddlat'],
                    dbase['ddlon'], dbase['groupby'])
    mdbcur.execute(sql)
    print "There were {0} records found in {1}".format(mdbcur.rowcount,
                                                       db)
    result = mdbcur.fetchall()

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

constr = "dbname={0} user={1}".format(PG_DB, PG_USER)            
pgconn = psycopg2.connect(constr)
pgcur = pgconn.cursor()

sql = """DROP TABLE IF EXISTS spatial_tmp"""
pgcur.execute(sql)

sql = """CREATE TABLE spatial_tmp
(
  id serial NOT NULL,
  prj_cd character(13) NOT NULL,
  sam character varying(30),
  geom geometry(Point,4326) NOT NULL
)
"""
pgcur.execute(sql)
pgconn.commit()

args = ([{'prj_cd':x[1], 'sam':x[2], 'ddlat':x[3], 'ddlon':x[4]}
         for x in samplepoints])

sql = """INSERT INTO spatial_tmp (prj_cd, sam, geom)
         VALUES(%(prj_cd)s, %(sam)s,
         ST_SetSRID(ST_MakePoint(%(ddlon)s, %(ddlat)s), 4326));"""

pgcur.executemany(sql, args)
pgconn.commit()

#clear out the old data
sql = """DELETE FROM pjtk2_samplepoint"""
pgcur.execute(sql)

#now update pjtk2_samplepoint by joining on project code (don't have
# to worry about projects without spatial data or projects not in
# tracker (yet))
sql = """insert into pjtk2_samplepoint (project_id, sam, geom)
         select pjtk2_project.id as project_id, sam, geom from spatial_tmp 
         join pjtk2_project on pjtk2_project.prj_cd=spatial_tmp.prj_cd"""
pgcur.execute(sql)

#cleanup
sql = """DROP TABLE spatial_tmp"""
pgcur.execute(sql)
pgconn.commit()

pgcur.close()
pgconn.close()





