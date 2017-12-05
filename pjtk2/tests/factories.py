import factory
from datetime import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import GEOSGeometry

from pjtk2.models import *


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = 'John'
    last_name = 'Doe'
    #username = 'johndoe'
    username = factory.Sequence(lambda n: 'User {0}'.format(n))
    email = 'johndoe@hotmail.com'
    #admin = False
    password = 'abc'

    #from: http://www.rkblog.rk.edu.pl/w/p/
    #               using-factory-boy-django-application-tests/
    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class DBA_Factory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = 'Bill'
    last_name = 'Gates'
    #username = 'billgates'
    username = factory.Sequence(lambda n: 'DBA {0}'.format(n))
    email = 'microsoft@sucks.com'
    is_superuser = True
    is_active = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(DBA_Factory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class ManagerFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = 'Boss'
    last_name = 'Hogg'
    username = 'bosshogg'
    email = 'bosshogg@hotmail.com'
    #manager = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(DBA_Factory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class LakeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Lake
    lake = "Lake Huron"


class EmployeeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Employee
    user = factory.SubFactory(UserFactory)
    position = 'worker bee'
    role = 'employee'
    #lake = factory.SubFactory(LakeFactory)
    supervisor = None


class ProjTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ProjectType
    project_type = "Offshore Index"


class DatabaseFactory(factory.DjangoModelFactory):
    class Meta:
        model = Database
    master_database = "Offshore Master"
    path = "C:/Path/to/somedb.mdb"


class FamilyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Family
    id = factory.Sequence(lambda n:n)


class ProjectFactory(factory.DjangoModelFactory):
    '''year and slug are built by the project save method'''
    class Meta:
        model = Project

    prj_cd = "LHA_IA12_123"
    prj_nm = "Fake Project"
    #prj_ldr = "Bob Sakamano"
    prj_ldr = factory.SubFactory(UserFactory)
    field_ldr = factory.SubFactory(UserFactory)
    abstract = "This is the abstract for a fake project"
    comment = "This is a comment for our fake project"
    risk = "none"
    project_type = factory.SubFactory(ProjTypeFactory)
    master_database = factory.SubFactory(DatabaseFactory)
    owner = factory.SubFactory(UserFactory)
    dba = factory.SubFactory(DBA_Factory)
    salary = None
    odoe = None

    lake = factory.SubFactory(LakeFactory)


    @factory.lazy_attribute
    def prj_date0(a):
        yr = a.prj_cd[6:8]
        year = '19' + yr if int(yr)>50 else '20' + yr
        datestring = "January 15, {0}".format(year)
        prj_date0 = datetime.datetime.strptime(datestring, "%B %d, %Y")
        return(prj_date0)

    @factory.lazy_attribute
    def prj_date1(a):
        yr = a.prj_cd[6:8]
        year = '19' + yr if int(yr)>50 else '20' + yr
        datestring = "January 16, {0}".format(year)
        prj_date1 = datetime.datetime.strptime(datestring, "%B %d, %Y")
        return(prj_date1)

    @factory.lazy_attribute
    def year(a):
        'calculate a based on project code'
        yr = a.prj_cd[6:8]
        year = '19' + yr if int(yr)>50 else '20' + yr
        return(year)


class ProjectSisters(factory.DjangoModelFactory):
    class Meta:
        model = ProjectSisters

    family = factory.SubFactory(FamilyFactory)
    project = factory.SubFactory(ProjectFactory)


class MilestoneFactory(factory.DjangoModelFactory):
    class Meta:
        model = Milestone

    '''Look-up table of reporting milestone'''
    label = "Completion Report"
    label_abbrev = factory.Sequence(lambda n: 'milestone {0}'.format(n))
    shared = False
    category = "Core"
    order = 1


class ProjectMilestonesFactory(factory.DjangoModelFactory):
    class Meta:
        model = ProjectMilestones

    '''list of reporting requirements for each project'''
    project = factory.SubFactory(ProjectFactory)
    milestone = factory.SubFactory(MilestoneFactory)


class ReportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Report
    current = True
    #projectreport = factory.SubFactory(ProjectMilestonesFactory)
    report_path = "some/fake/file.txt"
    #uploaded_by = "Bob"
    uploaded_by = factory.SubFactory(UserFactory)
    report_hash = "1234"

    #@factory.post_generation
    #def projectreport(self, create, extracted, **kwargs):
    #    if not create:
    #        # Simple build, do nothing.
    #        return
    #
    #    if extracted:
    #        try:
    #            for pmst in extracted:
    #                self.projectmilestones.add(pmst)
    #        except TypeError:
    #            self.projectmilestones.add(extracted)



class AssociatedFactory(factory.DjangoModelFactory):
    class Meta:
        model = AssociatedFile
    current = True
    project = factory.SubFactory(Project)
    file_path = "some/fake/file.txt"
    #uploaded_by = "Bob"
    uploaded_by = factory.SubFactory(UserFactory)
    report_hash = "1234"


class SamplePointFactory(factory.DjangoModelFactory):
    class Meta:
        model = SamplePoint

    project = factory.SubFactory(ProjectFactory)
    sam = '123'
    #centroid of grid 2826
    geom = GEOSGeometry('POINT(-82.0416679344936 44.041664015521)')
