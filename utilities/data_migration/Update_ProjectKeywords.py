'''=============================================================
c:/1work/Python/djcode/pjtk2/migration/Update_ProjectKeywords.py
Created: 08 Jul 2014 15:41:07


DESCRIPTION:

This script is updates the keywords for projects in project tracker.
Keywords were associated with a project based on the contents of their
project name and description.  Candidate keywords were identified by
looking for commonly used places, regions, rivers, and protocols that
occurred regularly in existing entries.  Additionally, a keyword was
often associated with the database that contained the source data
(offshore, nearshore, smallfish etc.).  Finally, species where added
to each project by examining the top 4 species that were most commonly
caught and sampled in each project.  The dictionary of species
keywords was created by a sister script
[~/pjtk2/migration/make_spc_keyword_dict.py] and written out to json.


A. Cottrill
=============================================================

'''

import django_settings
import json
from pjtk2.models import Project

spc_keywords = json.load(open('c:/1work/scrapbook/spc_keywords.json'))

#projects = Project.objects.all()

for prj_cd, kwds in spc_keywords.items():
    try:
        project = Project.objects.get(prj_cd=prj_cd)
    except:
        #Print out project codes we can't find
        print(prj_cd)
    for kwd in kwds:
        project.tags.add(str(kwd))
    project.save()


#  #Project Codes:
#  CH - Commerical Harvest

projects = Project.objects.filter(prj_cd__contains='_CH')
print('{} CH project found'.format(projects.count()))
for project in projects:
    project.tags.add('commercial harvest')
    project.save()

#  SS - Stock Status
projects = Project.objects.filter(prj_cd__contains='_SS')
print('{} SS project found'.format(projects.count()))
for project in projects:
    project.tags.add('stock status')
    project.save()


#  # these are the keywords that I can think of, quickly find in the
#  # project tracker database loop over each one, find projects that have
#  # that keyword in its name or comment and add that keyword to those
#  # projects.
kwds = [
'Tobermory',
'Kincardine',
'Goderich',
'Bayfield',
'Port Elgin',
'Port Albert',
'Southampton',
'Oliphant',
'Stokes Bay',
'Sarnia',
'Grand Bend',
'South Bay',
'Providence Bay',
'Meldrum Bay',
'Gore Bay',
'Little Current',
'Blind River',
'Frazer Bay',
'Iroquois Bay',
'Britt',
'Killarney',
'Parry Sound',
'Limestone Islands',
'Grand Bank',
'Bruce Archipelago',
'Colpoys Bay',
'Owen Sound',
'Lion\'s Head',
'Cape Rich',
'Meaford',
'Thornbury',
'Nottawasaga Bay',
'Collingwood',
'Wasaga Beach',
'Christian Island',
'Severn Sound',
'Watcher Islands',
'North Channel',
'Georgian Bay',
'Douglas Point',
'Clapperton Island',
'Heywood Island',
'Bay of Islands',
'MacGregor Bay',
'South Baymouth',
'Pointe au Baril',
'Saugeen River',
'Denny\'s Dam',
'Sauble River',
'Maitland River',
'Sydenham River',
'Moon River',
'French River',
'Whitefish River',
'Shebeshekong River',
'Magnetewan River',
'Mushquash River',
'Shawanaga River',
'Spanish River',
'Serpent River',
'Nottawasaga River',
'Key River',
'Mississagi River',
'Bighead River',
'Beaver River',
'Pretty River',
'Whitefish Falls',
'Gravelly Bay',
'Manitoulin Island',
'port creel',
'access creel',
'roving creel',
'boat count',
'derby sampling',
'FLIN',
'SMIN',
'ESTN',
'SWIN',
'SMIN',
'aging',
'cwt',
'Contaminants']

#now loop over the keywords, find projects that have those keywords in
#either their project name or project description (comment) and add
#the key workd to each of those projects.
for kwd in kwds:
    projects = (Project.objects.filter(prj_nm__icontains=kwd) |
                Project.objects.filter(comment__icontains=kwd))
    for project in projects:
        project.tags.add(kwd.lower())
        project.save()
print("Done!!")
