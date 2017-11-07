'''=============================================================
c:/1work/Python/djcode/pjtk2/migration/ProjectKeywords.py
Created: 08 Jul 2014 14:48:36

DESCRIPTION:

This spript creates a dictionary of project codes and species names
that will be used as keywords in the new version of project tracker.
Species where identified for each project by examining the top 4
species that were most commonly caught and sampled in each project.
This dictionary is then written out to a json file that can be read in
and used to update pjtk2.

A. Cottrill
=============================================================

'''


import pyodbc
import json

def get_key_spc(fn123, N=4):
    """a function to build list of species observed in each project.
    fn123 is a pyodbc recordset that must contain the fields prj_cd,
    spc, biocnt and catcnt.  The union of the top N species in the
    catch count and biocnts fields are returned for each project code
    in fn123.

    Returns a dictionary with prj_cd as key and list of species codes
    as the values.

    """
    projects = list(set([x[0] for x in fn123]))

    key_spc = dict()

    for prj_cd in projects:
        prj = []
        [prj.append(x) for x in fn123 if x[0]==prj_cd]
        tmp = [x for x in prj if x[2] is not None]

        if len(tmp)<=N:
            biocnts = [x[1] for x in tmp]
        else:
            try:
                biocnts = [x[1] for x in sorted(tmp, key=lambda e : e[2],
                                                reverse=True)[:N]]
            except:
                biocnts = []

        tmp = [x for x in prj if x[3] is not None]
        if len(tmp)<=N:
            catcnts = [x[1] for x in tmp]
        else:
            catcnts = [x[1] for x in sorted(tmp, key=lambda e : e[3],
                                        reverse=True)[:N]]

        key_spc[prj_cd] = list(set(biocnts).union(catcnts))

    return(key_spc)


def spc_code2name(projects, spc_dict, dbase=None):
    """A helper function to take the species codes contained in the
    project dictionaries and convert them to lists of species names.
    Optionally, the database name is also added to list of species names -
    it will be a key word too and is dertemined by the source database.

    Arguments:
    - `projects`:
    - `spc_dict`:
    - `dbase`:

    """

    for prj in projects:
        spc_codes = projects.get(prj)
        spc_nms = []
        if dbase:
            spc_nms.append(dbase)
        for spc in spc_codes:
            spc_nms.append(spc_dict.get(spc))
        projects[prj]=spc_nms
    return(projects)




#===============================
#   SPC Dict

dbase = 'Z:/Data Warehouse/Utilities/Code Tables/LookupTables/LookupTables.mdb'
constring = "DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}".format(dbase)

con = pyodbc.connect(constring)
cur = con.cursor()

sql = '''SELECT SPC, SPC_NM FROM SPC;'''

cur.execute(sql)
results = cur.fetchall()
for rec in results[:5]:
    print(rec)

spc_dict = {x[0]:x[1].lower() for x in results}




#===============================
#   OFFSHORE

dbase = "C:/1work/Databases/IA_OFFSHORE_Master.mdb"
constring = "DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}".format(dbase)

con = pyodbc.connect(constring)
cur = con.cursor()

sql = '''SELECT PRJ_CD, SPC, Sum(offshore_fn123.BIOCNT) AS Biocnt, Sum(Offshore_FN123.CATCNT) AS Catcnt
FROM Offshore_FN123 GROUP BY PRJ_CD, SPC ORDER BY PRJ_CD'''

cur.execute(sql)
results = cur.fetchall()

cur.close()
con.close()

offshore = get_key_spc(results)
offshore = spc_code2name(offshore, spc_dict, 'offshore index')
for prj in list(offshore.keys())[:5]:
    print(prj, offshore[prj])



#===============================
#   NEARSHORE

dbase = "C:/1work/Databases/IA_NearShore_Master.mdb"
constring = "DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}".format(dbase)

con = pyodbc.connect(constring)
cur = con.cursor()

sql = '''SELECT PRJ_CD, SPC, Sum(IA123.BIOCNT) AS Biocnt, Sum(IA123.CATCNT) AS Catcnt
FROM IA123 GROUP BY PRJ_CD, SPC ORDER BY PRJ_CD'''

cur.execute(sql)
results = cur.fetchall()

cur.close()
con.close()

nearshore = get_key_spc(results)
nearshore = spc_code2name(nearshore, spc_dict, 'nearshore index')
for prj in list(nearshore.keys())[:5]:
    print(prj, nearshore[prj])


#===============================
#   CF

dbase = "C:/1work/Databases/CF_Master.mdb"
constring = "DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}".format(dbase)

con = pyodbc.connect(constring)
cur = con.cursor()

sql = '''SELECT PRJ_CD, SPC, Sum(Final_FN123.BIOCNT) AS Biocnt, Sum(Final_FN123.CATCNT) AS Catcnt
FROM Final_FN123 GROUP BY PRJ_CD, SPC ORDER BY PRJ_CD'''

cur.execute(sql)
results = cur.fetchall()
for rec in results[:5]:
    print(rec)
cur.close()
con.close()

cf = get_key_spc(results)
cf = spc_code2name(cf, spc_dict, 'catch sampling')

for prj in list(cf.keys())[:5]:
    print(prj, cf[prj])




#===============================
#   SPORT FISH

dbase = "C:/1work/Databases/SF_MASTER_working.mdb"
constring = "DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}".format(dbase)

con = pyodbc.connect(constring)
cur = con.cursor()

sql = '''SELECT PRJ_CD, SPC, Sum(FN123.BIOCNT) AS Biocnt, Sum(FN123.CATCNT) AS Catcnt
FROM FN123 GROUP BY PRJ_CD, SPC ORDER BY PRJ_CD'''

cur.execute(sql)
results = cur.fetchall()
for rec in results[:5]:
    print(rec)

cur.close()
con.close()

sportfish = get_key_spc(results)
sportfish = spc_code2name(sportfish, spc_dict, 'sportfish monitoring')
for prj in list(sportfish.keys())[:5]:
    print(prj, sportfish[prj])


#===============================
#   SMALLFISH

dbase = "C:/1work/Databases/COA_Nearshore_Smallfish.mdb"
constring = "DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}".format(dbase)

con = pyodbc.connect(constring)
cur = con.cursor()

sql = '''SELECT PRJ_CD, SPC, Sum([123].BIOCNT) AS Biocnt, Sum([123].CATCNT) AS Catcnt
FROM [123] GROUP BY PRJ_CD, SPC ORDER BY PRJ_CD'''

cur.execute(sql)
results = cur.fetchall()
for rec in results[:5]:
    print(rec)
cur.close()
con.close()

smallfish = get_key_spc(results)
smallfish = spc_code2name(smallfish, spc_dict, 'smallfish monitoring')
for prj in list(smallfish.keys())[:5]:
    print(prj, smallfish[prj])


#===============================
#   SPORT CREEL

dbase = "C:/1work/Databases/Work_SC_Master.mdb"
constring = "DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}".format(dbase)

con = pyodbc.connect(constring)
cur = con.cursor()

sql = '''SELECT PRJ_CD, SPC, Sum([Final_FN123].BIOCNT) AS Biocnt,
Sum([Final_FN123].CATCNT) AS Catcnt
FROM [Final_FN123] GROUP BY PRJ_CD, SPC ORDER BY PRJ_CD'''

cur.execute(sql)
results = cur.fetchall()
for rec in results[:5]:
    print(rec)

cur.close()
con.close()

creels = get_key_spc(results)
creels = spc_code2name(creels, spc_dict, 'creel survey')
for prj in list(creels.keys())[:5]:
    print(prj, creels[prj])


#===============================
#   FISHWAYS

dbase = "Z:/Data Warehouse/Assessment/Fishway/Fishway_Master.mdb"
constring = "DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}".format(dbase)

con = pyodbc.connect(constring)
cur = con.cursor()

sql = '''SELECT PRJ_CD, SPC, Sum([IM_123].BIOCNT) AS Biocnt,
Sum([IM_123].CATCNT) AS Catcnt
FROM [IM_123] GROUP BY PRJ_CD, SPC ORDER BY PRJ_CD'''

cur.execute(sql)
results = cur.fetchall()
for rec in results[:5]:
    print(rec)
cur.close()
con.close()

fishways = get_key_spc(results)
fishways = spc_code2name(fishways, spc_dict, 'fishway monitoring')cf

for prj in list(fishways.keys())[:5]:
    print(prj, fishways[prj])




#===============================
#   FISH STOCKING

#fish stocking is a little different - just summarize all species
#associated with each project code.

dbase = "C:/1work/Databases/FS_Master.mdb"
constring = "DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}".format(dbase)

con = pyodbc.connect(constring)
cur = con.cursor()

sql = ''' SELECT PRJ_CD, Spc FROM FS_Events GROUP BY PRJ_CD, Spc'''

cur.execute(sql)
results = cur.fetchall()
for rec in results[:5]:
    print(rec)

cur.close()
con.close()


projects = list(set([x[0] for x in results]))

stocking = dict()
for prj in projects:
    spc = [x for x in results if x[0]==prj]
    tmp = [x[1] for x in spc]
    stocking[prj] = tmp

stocking = spc_code2name(stocking, spc_dict, 'fish stocking')

for prj in list(stocking.keys())[:5]:
    print(prj, stocking[prj])



#===============================
#      EXPORT THEM!!

#now combine all of the project specific keyword dictionaries into a
#single dictionary, and write it out to a file that we can read in
#after loading our django settings.

spc_keywords = {}
spc_keywords.update(offshore)
spc_keywords.update(nearshore)
spc_keywords.update(cf)
spc_keywords.update(smallfish)
spc_keywords.update(sportfish)
spc_keywords.update(creels)
spc_keywords.update(stocking)
spc_keywords.update(fishways)

outfile = 'c:/1work/scrapbook/spc_keywords.json'
json.dump(spc_keywords, open(outfile,'w'))
