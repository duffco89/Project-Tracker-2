import django_settings

import csv
import os

from pjtk2.models import ProjectType, ProjectProtocol


HERE = "c:/Users/COTTRILLAD/1work/Python/djcode/pjtk2/pjtk2/utils"

# project types:

ptypes = []
fname = os.path.join(HERE, "project_types_march2020.csv")
with open(fname, newline="") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        ptypes.append(row)


protocols = []
fname = os.path.join(HERE, "protocols_march_2020.csv")
with open(fname, newline="") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        protocols.append(row)


# now create oru new objects and add them to the database

scope_lookup = {
    "Fishery Dependent": "FD",
    "Fishery Independent": "FI",
    "Multiple Sources": "MS",
}

items = []
for item in ptypes:
    x = ProjectType(
        scope=scope_lookup[item[0]], project_type=item[1], field_component=bool(item[2])
    )
    items.append(x)
# clear out the old
ProjectType.bulk_create(items)

project_types = {x.project_type: x for x in ProjectType.objects.all()}

items = []
for item in protocols:
    x = Protocol(
        project_type=project_types.get(item[0]), protocol_label=item[1], abbrev=item[2]
    )
    items.append(x)

Protocols.bulk_create(items)

# ===============================================
#       PROJECT IMAGES

# we need to get all of the image files and their captions from the
# annual report directory:

src_dir = (
    "C:/Users/COTTRILLAD/1work/ProjectMgt/Annual_Project_Report/figures/huronfigures"
)
figure_catalog = os.path.join(src_dir, "figure_catalog.csv")

trg_dir = "C:/Users/COTTRILLAD/1work/Python/djcode/pjtk2/uploads/project_images"


# get a prj_cd_cache to minimize queries
# prj_cd_catche = {x.prj_cd: x  for x in Project.objects.all()}

# read in the figure cataloge
figures = []
with open(figure_catalog, newline="") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        figures.append(row)


# for each figure in the figure cataloge, create a directory in the
# target directory if it does not exist and copy the file from the src
# dirctory to trg directory, and create a project image object using the caption from the cataloge.
# the image path that needs to be saved with the image will be of the form:
# project_images/{prj_cd}/{file_name}


# ===============================================
#    PROJECT SAMPLE POINTS

# the sample points are very similar to the project images read in the
# points (either in spreadsheet or csv format), lookup the project
# code, create the geos Point object, and create the sample points.

from django.contrib.gis.geos import GEOSGeometry


src_file = (
    "C:/Users/COTTRILLAD/1work/ProjectMgt/Annual_Project_Report/"
    + "2016_Sample_points.csv"
)
pts = []
with open(src_file, newline="") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        project = project_cache.get(pt[0])
        label = pt[1]
        wkt = "POINT({} {})".format(pt[3], pt[2])
        geopt = GEOSGeometry(wkt, srid=4326)
        pts.append(SamplePoint(project=project, label=label, geom=geopt))

SamplePoint.objects.bulk_create(pts)

# don't forget to:
#  - update the spatial data from Grandwazoo
#  - update the convex hull for each project
# resave each point to populate the pop-up text


# =========================================
#     LAKE SUPERIOR IMAGE DIRECORIES

xlsx_file = (
    "C:/Users/COTTRILLAD/1work/ProjectMgt/Annual_Project_Report/"
    + "figures/superiorfigures/figure_catalog.xlsx"
)
wb = openpyxl.load_workbook(xlsx_file)
ws = wb.get_sheet_by_name("figure_catalog")
image_attrs = []

for row in ws.iter_rows():
    image_attrs.append(
        {"prj_cd": row[0].value, "fname": row[1].value, "caption": row[2].value}
    )
# remove the column heading
image_attrs.pop(0)

# lets make sure tha all of our project codes are real projects:


pc = set([x["prj_cd"] for x in image_attrs])
for x in pc:
    if project_cache.get(x) is None:
        print(x)

# now - loop over our image attributes and verify the project directory exists

IMG_SRC_DIR = (
    "C:/Users/COTTRILLAD/1work/ProjectMgt/Annual_Project_Report/figures/superiorfigures"
)

for x in pc:
    img_dir = os.path.join(IMG_SRC_DIR, x)
    if os.path.isdir(img_dir) is False:
        print("Can't find directory for ({})".format(x))


# now loop over the files in the spreadsheets and see how many don't exists:
# If a file cannot be found, report the files that were found:
# looking for:
# >
# >


for img in image_attrs:
    prj_cd = img.get("prj_cd")
    fname = img.get("fname")
    if fname.endswith("pdf") or fname.endswith("docx"):
        print("{}/{}?".format(prj_cd, fname))
    img_path = os.path.join(IMG_SRC_DIR, prj_cd, fname)
    if os.path.exists(img_path) is False:
        print("\nUnable to find:\n{}/{}".format(prj_cd, fname))
        found = os.listdir(os.path.split(img_path)[0])
        if found:
            print("found:")
            [print("{}/{}".format(prj_cd, x)) for x in found]


# to update the project types and project protocols, we are going to
# need a couple of caches:
protocol_cache = {x.abbrev: x for x in ProjectProtocol.objects.all()}

project_cache = {x.prj_cd: x for x in Project.all_objects.all()}

projecttype_cache = {x.project_type: x for x in ProjectType.objects.all()}


projects = Project.objects.filter(prj_cd__contains="_CH")
protocol = protocol_cache["DCR"]

for project in projects:
    project.protocol = protocol
    project.project_type = protocol.project_type
    project.save()


# fish Stocking - all rehab for now.
projects = Project.objects.filter(prj_cd__contains="_FS")
protocol = protocol_cache["FSR"]

for project in projects:
    project.protocol = protocol
    project.project_type = protocol.project_type
    project.save()


# Catch Sampling - all onboard for now


def update_projtypes_and_protocols(ptype, protocol):
    projects = Project.objects.filter(prj_cd__contains=ptype).filter(
        project_type__isnull=True
    )
    print("found {} {} projects.".format(len(projects), ptype))
    protocol = protocol_cache[protocol]

    for project in projects:
        project.protocol = protocol
        project.project_type = protocol.project_type
        project.save()


update_projtypes_and_protocols("_CF", "CFO")
update_projtypes_and_protocols("_XX", "CFO")
update_projtypes_and_protocols("_CD", "CFO")

# contamiant collections
update_projtypes_and_protocols("_CC", "CC")


# Sport Creels - roving for now
update_projtypes_and_protocols("_SC", "SCR")


# Fishways
update_projtypes_and_protocols("_IM", "FMA")


# Telemetry
update_projtypes_and_protocols("_TE", "TE")

# CWT Recoveries
update_projtypes_and_protocols("_CWT", "CWT")

update_projtypes_and_protocols("_TR", "TR")


# Lamprey monitoring and recovery
update_projtypes_and_protocols("_LAM", "IJC")


# AR - Assessment Reporting
# BN - Benthic Sampling
# SD - Angler Diary Programs
# SS - status of stocks
# HA - Hydroaccoustic Assessment


# nearshore proejcts with UNKN PROTOCOL:

# PRJ_CD	protocol
# LHA_IA08_260	UNKN
# LHA_IA09_260	UNKN
# LHA_IA09_261	UNKN
# LHA_IS93_013	UNKN
# LHA_IS94_013	UNKN
# LHA_IS95_013	UNKN
# LHA_IS96_013	UNKN

# nearshore projects in the amst that do not appear to be in project tracker:

# PRJ_CD	protocol
# LHA_IA09_259	SMIN
# LHA_IA09_261	UNKN
# LHA_IA10_262	SMIN
# LHA_IA11_300	EF
# LHA_IA14_249	SMIN


prj_cds = ["LHA_IA13_RND", "LHA_IA11_LEG", "LHA_IA12_LEG", "LHA_IA13_LEG"]

project_type = ProjectType.objects.get(project_type="Synthesis")

for prj_cd in prj_cds:
    project = project_cache.get(prj_cd)
    project.project_type = project_type
    project.save()


protocol_cache = {x.abbrev: x for x in ProjectProtocol.objects.all()}

missing_projects = []
missing_protocols = []
for item in todos:
    project = project_cache.get(item[0])
    protocol = protocol_cache.get(item[1])
    if project is None:
        missing_projects.append(item[0])
    if protocol is None:
        missing_protocols.append(item[1])
    if protocol and project:
        project.protocol = protocol
        project.project_type = protocol.project_type
        project.save()

print("{} missing projects".format(len(missing_projects)))
print("{} missing protocols".format(len(missing_protocols)))

# ptype = projecttype_cache.get("Synthesis and Analysis")
# project = project_cache.get("LHA_FA16_MAT")
# project.project_type = ptype
# project.save()

todos = [
    ("LHA_IA13_RND", "SAA"),
    ("LHA_IA13_LEG", "SAA"),
    ("LHA_IA12_LEG", "SAA"),
    ("LHA_IA11_LEG", "SAA"),
    ("LHA_FA16_MAT", "SAA"),
]

todos = [
    ("LHA_AR16_001", "NFSR"),
    ("LHA_AR17_001", "NFSR"),
    ("LHA_AR18_001", "NFSR"),
    ("LHA_AR19_DEP", "SSA"),
    ("LHA_AR19_001", "NFSR"),
    ("LHA_AS14_081", "AE"),
    ("LHA_AS15_091", "AE"),
    ("LHA_AS15_081", "AE"),
    ("LHA_AS17_334", "AE"),
    ("LHA_BN00_001", "BEN"),
    ("LHA_BN01_001", "BEN"),
    ("LHA_BN02_001", "BEN"),
    ("LHA_BN03_001", "BEN"),
    ("LHA_BN04_001", "BEN"),
    ("LHA_BN05_001", "BEN"),
    ("LHA_BN07_001", "BEN"),
    ("LHA_BN08_001", "BEN"),
    ("LHA_BN09_001", "BEN"),
    ("LHA_BS96_101", "BS"),
    ("LHA_BS97_101", "BS"),
    ("LHA_BS05_101", "BS"),
    ("LHA_BS06_101", "BS"),
    ("LHA_CW09_001", "CWT"),
    ("LHA_IL17_T05", "WFTW"),
    ("LHA_IL17_T07", "WFTW"),
    ("LHA_IL18_T05", "WFTW"),
    ("LHA_IL19_T05", "WFTW"),
    ("LHA_SC93_005", "SC"),
    ("LHA_SC03_111", "SCR"),
    ("LHA_SC03_110", "SCA"),
    ("LHA_SC01_401", "SFD"),
    ("LHA_SS06_001", "SS"),
    ("LHA_SS07_001", "SS"),
    ("LHA_SS08_001", "SS"),
    ("LHA_SS09_001", "SS"),
    ("LHA_SS10_001", "SS"),
    ("LHA_SS11_001", "SS"),
    ("LHA_VC02_001", "SF"),
    ("LHA_XF01_031", "LSA"),
    ("LHA_XF15_031", "LSA"),
    ("LHA_XF16_031", "LSA"),
    ("LHA_XF17_031", "LSA"),
    ("LHA_XF18_031", "LSA"),
    ("LHA_XF19_031", "LSA"),
]


projects = Project.all_objects.filter(
    project_type__project_type="Sport Fish Collection"
)

protocol = protocol_cache.get("SF")

for project in projects:
    project.protocol = protocol
    project.project_type = protocol.project_type
    project.save()


projects = Project.all_objects.filter(protocol__abbrev="SCR").filter(
    prj_nm__icontains="access"
)

protocol = protocol_cache.get("SCA")
for project in projects:
    project.protocol = protocol
    project.save()


projects = Project.all_objects.filter(protocol__abbrev="SF").filter(
    prj_nm__icontains="volunteer"
)
protocol = protocol_cache.get("CVC")
for project in projects:
    project.protocol = protocol
    project.save()

from pjtk2.models import Project
from django.db.models import Count, F
from django.contrib.postgres.search import SearchQuery, SearchVector

from django.db import connection


term = "maxilla"
query_count0 = len(connection.queries)
projects = Project.objects.annotate(
    search=SearchVector("prj_nm", "abstract", "comment")
).filter(search=SearchQuery(term))

projects.count()
print("found {} projects".format(projects.count()))


query_count0 = len(connection.queries)
# calculate our facets by lake:
lakes = (
    projects.select_related("lake")
    .all()
    .values(lakeName=F("lake__lake_name"), lakeAbbrev=F("lake__abbrev"))
    .order_by("lakeName")
    .annotate(N=Count("lakeName"))
)
print("By Lakes:")
for x in lakes:
    print(x)
query_count1 = len(connection.queries)
print("queries run: {}".format((query_count1 - query_count0)))


project_types = (
    projects.select_related("project_type")
    .all()
    .values("project_type__project_type")
    .order_by("project_type")
    .annotate(N=Count("project_type"))
)

print("By Project Type:")
for x in project_types:
    print(x)


project_scope = (
    projects.select_related("project_type")
    .all()
    .values(projScope=F("project_type__scope"))
    .order_by("project_type__scope")
    .annotate(N=Count("project_type__scope"))
)
scope_lookup = dict(ProjectType.PROJECT_SCOPE_CHOICES)
for scope in project_scope:
    scope["name"] = scope_lookup.get(scope["projScope"])


print("By Project Scope:")
for x in project_scope:
    print(x)


project_field_component = (
    projects.select_related("project_type")
    .all()
    .values("project_type__field_component")
    .order_by("project_type__field_component")
    .annotate(N=Count("project_type__field_component"))
)
print("Field Component")
for x in project_field_component:
    print(x)

query_count1 = len(connection.queries)
print("queries run: {}".format((query_count1 - query_count0)))


protocols = (
    projects.select_related("protocol")
    .all()
    .values(projProtocol=F("protocol__protocol"), protocolAbbrev=F("protocol__abbrev"))
    .order_by("protocol")
    .annotate(N=Count("protocol"))
)
print("Protocols")
for x in protocols:
    print(x)

query_count1 = len(connection.queries)
print("queries run: {}".format((query_count1 - query_count0)))
