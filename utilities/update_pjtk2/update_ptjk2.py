"""=============================================================
 c:/Users/COTTRILLAD/1work/Python/djcode/pjtk2/pjtk2/utils/update_pjtk2/update_ptjk2.py
 Created: 13 Mar 2020 10:02:46

 DESCRIPTION:

  This file migrates an old version of project tracker to a new,
  merged version that accomodates multiple lakes.

 A. Cottrill
=============================================================

"""
import csv
import os
import openpyxl
import pprint
import psycopg2
from shutil import copyfile

import django_settings

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry

from common.models import Lake
from pjtk2.models import (
    Employee,
    Milestone,
    Database,
    ProjectType,
    ProjectProtocol,
    Project,
    ProjectImage,
    FundingSource,
    ProjectFunding,
    SamplePoint,
    ProjectMilestones,
    Report,
    AssociatedFile,
    Bookmark,
    Family,
    ProjectSisters,
    Message,
    Messages2Users,
)

# import .pjtk2_update_utils as utils


HERE = "c:/Users/COTTRILLAD/1work/Python/djcode/pjtk2/pjtk2/utils"

# this will differ depending on which Lake we are migrating:
# ROOT_SRC = "X:/djcode/pjtk2"
ROOT_SRC = "X:/djcode/pjtk2_ls"


SRC_DIR = os.path.join(ROOT_SRC, "uploads")
TRG_DIR = "C:/Users/COTTRILLAD/1work/Python/djcode/pjtk2/uploads"

PGPARS = {
    "HOST": "***REMOVED***",
    "DBNAME": "superior",
    "USER": os.getenv("PGUSER"),
    "PASSWORD": os.getenv("PGPASSWORD"),
}


pp = pprint.PrettyPrinter(indent=4)


# ===============================
#          LAKES

# lakes is an oddball - it now comes from a different app and includes
# additional fields.  make sure the lake we are migrating exists int
# the database before we go any further:

lake_cache = {x.lake_name: x for x in Lake.objects.all()}


# ===============================
#          USERS


User = get_user_model()
user_cache = {x.username: x for x in User.objects.all()}
users = get_users(PGPARS)
# we only want to create users if they don't already exist.  we will
# email them links to the reset password page afterwords so they they
# are forced to create a new one.
items = []
for user in users:
    username = user["username"]
    if user_cache.get(username) is None:
        print("Creating user:{}".format(username))
        items.append(User(**user))
User.objects.bulk_create(items)

# get our updated user cache for the rest of the queries:
user_cache = {x.username: x for x in User.objects.all()}


# ===============================
#          EMPLOYEES
employees = get_employees(PGPARS)
employee_cache = {x.user.username: x for x in Employee.objects.all()}
# we only want to create employees if they don't already exist.  we will
# email them links to the reset password page afterwords so they they
# are forced to create a new one.
for person in employees:
    employee_name = person.pop("employee")
    supervisor_name = person.pop("supervisor")
    employee = employee_cache.get(employee_name)
    supervisor = employee_cache.get(supervisor_name)
    if employee is None:
        print("Creating employee: {}".format(employee_name))
        user = user_cache.get(employee_name)
        if user is None:
            print("unable to find user: {}".format(employee_name))
        else:
            person["user"] = user
            if supervisor:
                person["supervisor"] = supervisor
            Employee(**person).save()


# ===============================
#          MILESTONES

# NOTE: costome model manager!!

milestones = get_milestones(PGPARS)
milestone_cache = {x.label_abbrev: x for x in Milestone.allmilestones.all()}
items = []
for ms in milestones:
    label = ms["label_abbrev"]
    if milestone_cache.get(label) is None:
        print("Creating Milestone: {}".format(label))
        Milestone(**ms).save()

# Milestone.objects.bulk_create(items)


# # ===============================
# #       PROJECT_TYPES - UPDATED
#
# projtype_cache = {x.project_type:x for x in ProjectType.objects.all()}
#
# ptypes = []
# fname = os.path.join(HERE, "project_types_march2020.csv")
# with open(fname, newline="") as csvfile:
#     csvreader = csv.reader(csvfile)
#     for row in csvreader:
#         ptypes.append(row)
#
# scope_lookup = {
#     "Fishery Dependent": "FD",
#     "Fishery Independent": "FI",
#     "Multiple Sources": "MS",
# }
#
# items = []
# for item in ptypes:
#     if projtype_cache.get(item[1]) is None:
#         print("Creating Project Type: {}".format(item[1]))
#         x = ProjectType(
#             scope=scope_lookup[item[0]], project_type=item[1], field_component=bool(item[2])
#         )
#         items.append(x)
# ProjectType.objects.bulk_create(items)
#
# projtype_cache = {x.project_type:x for x in ProjectType.objects.all()}
#
# # ===============================
# #       PROTOCOLS - NEW
#
#
#
# protocol_cache = {x.abbrev:x for x in ProjectProtocol.objects.all()}
#
# protocols = []
# fname = os.path.join(HERE, "protocols_march_2020.csv")
# with open(fname, newline="") as csvfile:
#     csvreader = csv.reader(csvfile)
#     for row in csvreader:
#         protocols.append(row)
#
# items = []
# for item in protocols:
#     if protocol_cache.get(item[2]) is None:
#         print("Creating Protocol: {}".format(item[2]))
#         project_type = projtype_cache[item[0]]
#         x = ProjectProtocol(
#             project_type=project_type, protocol=item[1], abbrev=item[2]
#         )
#         items.append(x)
#
# ProjectProtocol.objects.bulk_create(items)
#
# protocol_cache = {x.project_type:x for x in ProjectProtocol.objects.all()}


# ===============================
#          DATABASES


databases = get_databases(PGPARS)
database_cache = {x.master_database: x for x in Database.objects.all()}
items = []
for db in databases:
    label = db["master_database"]
    if database_cache.get(label) is None:
        print("Creating Database: {}".format(label))
        db.pop("id")
        items.append(Database(**db))

Database.objects.bulk_create(items)


# ==============================
#       PROJECTS
#  NOTE: custom model manager!

project_cache = {x.prj_cd: x for x in Project.all_objects.all()}

projects = get_projects(PGPARS)
items = []
for project in projects:
    if project_cache.get(project["prj_cd"]) is None:
        print("Creating {}({})".format(project["prj_nm"], project["prj_cd"]))
        lake_name = project.pop("lake")
        if lake_name:
            project["lake"] = lake_cache.get(lake_name)
        cancelled_by = project.pop("cancelled_by")
        if cancelled_by:
            project["cancelled_by"] = user_cache.get(cancelled_by)
        dba = project.pop("dba")
        if dba:
            project["dba"] = user_cache.get(dba)
        owner = project.pop("owner")
        if owner:
            project["owner"] = user_cache.get(owner)
        prj_ldr = project.pop("prj_ldr")
        if prj_ldr:
            project["prj_ldr"] = user_cache.get(prj_ldr)
        database = project.pop("database")
        if database:
            project["master_database"] = database_cache.get(database)
        field_ldr = project.pop("field_ldr")
        if field_ldr:
            project["field_ldr"] = user_cache.get(field_ldr)
        items.append(Project(**project))
Project.objects.bulk_create(items)

project_cache = {x.prj_cd: x for x in Project.all_objects.all()}


# ===============================
#     FUNDING SOURCES - NEW

# - like Lakes, we need to make sure that all of the funding sources
# - in our source database are in the target database.

funding_cache = {x.abbrev: x for x in FundingSource.objects.all()}
funding_sources = get_funding_sources(PGPARS)

for source in funding_sources:
    if funding_cache.get(source["funding"]) is None:
        print("Unable to find funding source for: {}".format(source["funding"]))


# ===============================
#     FUNDING  - NEW

funding = get_project_funding(PGPARS)
funding = [x for x in funding if x.get("odoe") or x.get("salary")]

# for each record in funding, create a record in project_funding with
# the corresponding reference to funding source.

for record in funding:
    project = project_cache.get(record.get("prj_cd"))
    source = funding_cache.get(record.get("funding"))
    if project is None or source is None:
        print("Oops! Problem with:", record)
    else:
        obj, created = ProjectFunding.objects.get_or_create(
            project=project, source=source, salary=record["salary"], odoe=record["odoe"]
        )
        obj.save()

# ==============================
#  PROJECT FIELD STAFF - NEW


# ==============================
#       PROJECT TAGS
tags = get_project_tags(PGPARS)

# convert our list of individual tag-project code pairs to a dictionary
# with project codes as keys and the tags as a list of stings.
tags_dict = {}
for tag in tags:
    prj_cd = tag["prj_cd"]
    name = tag["name"]
    if tags_dict.get(prj_cd) is None:
        tags_dict[prj_cd] = [name]
    else:
        mytags = tags_dict[prj_cd]
        mytags.append(name)
        tags_dict[prj_cd] = mytags

for key, value in tags_dict.items():
    project = project_cache.get(key)
    if project is None:
        print("Unable to find project with project = {}".format(key))
    else:
        project.tags.add(*value)
        project.save()
print("Done Adding tags to projects.")


# ==============================
#    PROJECT SAMPLE POINTS

# don't forget to get pts from 'workaround'
sample_points = get_project_sample_points(PGPARS)

pts = []
for pt in sample_points:
    prj_cd = pt.pop("prj_cd")
    project = project_cache.get(prj_cd)
    wkt = pt.pop("st_astext")
    geopt = GEOSGeometry(wkt, srid=4326)
    pts.append(SamplePoint(project=project, sam=pt["sam"], geom=geopt))

SamplePoint.objects.bulk_create(pts)

print("Done adding points from the database.")
# now read in the ones form the annual work around:

# sam can only be 30 characters long!
csv_file_dir = "C:/Users/COTTRILLAD/1work/ProjectMgt/Annual_Project_Report"
csv_files = [
    "2016_Sample_points.csv",
    "2017_Sample_points.csv",
    "2018_Sample_points.csv",
    "2019_Sample_points.csv",
]

pts = []
for csv_file in csv_files:
    src_file = os.path.join(csv_file_dir, csv_file)
    with open(src_file, newline="") as csvfile:
        print("Adding points from {}".format(csv_file))
        csvreader = csv.reader(csvfile)
        next(csvreader, None)  # skip the first row
        for row in csvreader:
            project = project_cache.get(row[0])
            sam = row[1][:30]
            wkt = "POINT({} {})".format(row[3], row[2])
            geopt = GEOSGeometry(wkt, srid=4326)
            pts.append(SamplePoint(project=project, sam=sam, geom=geopt))

SamplePoint.objects.bulk_create(pts)


# ==============================
#    PROJECT IMAGES - NEW
#
#
# in addition to creating the django objects we need to transfer the
# files to the correct location.

# xlsx_file = (
#    "C:/Users/COTTRILLAD/1work/ProjectMgt/Annual_Project_Report/"
#    + "figures/huronfigures/figure_catalog.xlsx"
# )


IMG_SRC_DIR = (
    "C:/Users/COTTRILLAD/1work/ProjectMgt/Annual_Project_Report/figures/superiorfigures"
)

xlsx_file = os.path.join(IMG_SRC_DIR, "figure_catalog.xlsx")

wb = openpyxl.load_workbook(xlsx_file)
ws = wb.get_sheet_by_name("figure_catalog")
image_attrs = []

for row in ws.iter_rows():
    image_attrs.append(
        {"prj_cd": row[0].value, "fname": row[1].value, "caption": row[2].value}
    )
# remove the column heading
image_attrs.pop(0)


# IMG_SRC_DIR = (
#    "C:/Users/COTTRILLAD/1work/ProjectMgt/Annual_Project_Report/figures/huronfigures"
# )


IMG_TRG_DIR = "C:/Users/COTTRILLAD/1work/Python/djcode/pjtk2/uploads/project_images"
# loop over the records in reports and copy the files form src to trg
image_order = 0
last_prj_cd = ""
images = []
for img in image_attrs:

    prj_cd = img.get("prj_cd")
    fname = img.get("fname")
    caption = img.get("caption")

    project = project_cache.get(prj_cd)

    if prj_cd == last_prj_cd:
        image_order += 1
    else:
        image_order = 0

    inreport = True if image_order < 2 else False

    images.append(
        ProjectImage(
            project=project,
            order=image_order,
            caption=caption,
            report=inreport,
            image_path=fname,
        )
    )

    last_prj_cd = prj_cd

    src = os.path.join(IMG_SRC_DIR, prj_cd, fname)
    trg = os.path.join(IMG_TRG_DIR, prj_cd, fname)
    # if the target directory does not exist - create it:
    if os.path.isdir(os.path.split(trg)[0]) is False:
        os.mkdir(os.path.split(trg)[0])
    copyfile(src, trg)

ProjectImage.objects.bulk_create(images)

print("Done copying project images.")


# ==============================
#     PROJECT MILESTONES


# don't forget to get pts from 'workaround'
proj_milestones = get_project_milestones(PGPARS)

milestones = []
for milestone in proj_milestones:
    prj_cd = milestone.pop("prj_cd")
    project = project_cache.get(prj_cd)
    ms_label = milestone.pop("label_abbrev")
    ms = milestone_cache[ms_label]
    milestones.append(
        ProjectMilestones(
            project=project,
            milestone=ms,
            completed=milestone["completed"],
            required=milestone["required"],
        )
    )

ProjectMilestones.objects.bulk_create(milestones)

print("Done adding project milestones to database.")

# now read in the ones form the annual work around:


# ==============================
#     REPORTS-AND-MILESTONES
#
# this query returns the reports and the milestones they are
# associated with/ we will need to copy the files to the correct
# location too including moving them into project specific folders
# (not sure how this will work with sisters)

reports = get_reports_and_milestones(PGPARS)

# for each record, get the corresponding project-milestone get or
# create the record, if it was created, save it, add the proejct
# milestone, and save it again.
for report in reports:
    myms = ProjectMilestones.objects.get(
        project__prj_cd=report["prj_cd"], milestone__label_abbrev=report["label_abbrev"]
    )
    uploaded_by = user_cache[report["uploaded_by"]]
    obj, created = Report.objects.get_or_create(
        current=report["current"],
        report_hash=report["report_hash"],
        report_path=report["report_path"],
        uploaded_by=uploaded_by,
        uploaded_on=report["uploaded_on"],
    )
    if created:
        obj.save()
    obj.projectreport.add(myms)
    obj.save()

print("Done adding reports to database. Now to transfer the files....")


# loop over the records in reports and copy the files form src to trg
for report in reports:
    src = os.path.join(SRC_DIR, report["report_path"])
    trg = os.path.join(TRG_DIR, report["report_path"])
    copyfile(src, trg)

print("Done copying reports.")


# ==============================
#      ASSOCIATED FILES
#
# in addition to creating the django objects we need to transfer the
# files to the correct location.
associated_files = get_associated_files(PGPARS)

items = []
for item in associated_files:
    prj_cd = item.pop("prj_cd")
    myuser = item.pop("uploaded_by")
    item["uploaded_by"] = user_cache[myuser]
    item["project"] = project_cache.get(prj_cd)
    items.append(AssociatedFile(**item))

AssociatedFile.objects.bulk_create(items)

print("Done adding associated files to database.  Now to transfer files...")

# loop over the records in reports and copy the files form src to trg
for item in associated_files:
    src = os.path.join(SRC_DIR, item["file_path"])
    trg = os.path.join(TRG_DIR, item["file_path"])
    # if the target directory does not exist - create it:
    if os.path.isdir(os.path.split(trg)[0]) is False:
        os.mkdir(os.path.split(trg)[0])
    copyfile(src, trg)

print("Done copying associated files.")


# ==============================
#        BOOKMARKS

bookmarks = get_bookmarks(PGPARS)
items = []
for bookmark in bookmarks:
    prj_cd = bookmark.pop("prj_cd")
    project = project_cache.get(prj_cd)
    username = bookmark.pop("username")
    myuser = user_cache.get(username)
    items.append(Bookmark(project=project, user=myuser, date=bookmark["date"]))

Bookmark.objects.bulk_create(items)

print("Done creating bookmarks.")


# ==============================
#        SISTERS
# get or create famillies as they come in

sisters = get_sisters(PGPARS)

family_ids = list(set([x["family_id"] for x in sisters]))

# for each value in family_ids, we are going to create a family, select
# the sisters taht have the same family is and append them to the
# database to ensure that family grouping remain intact.

items = []
for myid in family_ids:
    family = Family()
    family.save()
    mysisters = [x for x in sisters if x.get("family_id") == myid]
    for item in mysisters:
        project = project_cache.get(item["prj_cd"])
        items.append(ProjectSisters(project=project, family=family))
ProjectSisters.objects.bulk_create(items)

print("Done creating families and sisters.")


# ==============================
#        MESSAGES

messages = get_messages(PGPARS)

# for each message, creae a Message objects and save it.  then get the
# message2user objects for each one, create them, and add them to our
# message.

for msg in messages:
    pms = ProjectMilestones.objects.get(
        project__prj_cd=msg["prj_cd"], milestone__label_abbrev=msg["label_abbrev"]
    )
    message = Message(project_milestone=pms, level=msg["level"], msgtxt=msg["msgtxt"])
    message.save()
    msgs2users = get_messages2users(msg["msg_id"], PGPARS)
    for item in msgs2users:
        my_user = user_cache.get(item["username"])
        msg2user = Messages2Users(
            user=my_user, message=message, created=item["created"], read=item["read"]
        )
        msg2user.save()

print("Done creating messages and messages2users.")
