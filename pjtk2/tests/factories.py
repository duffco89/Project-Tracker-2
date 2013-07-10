import factory
from datetime import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from pjtk2.models import *


class UserFactory(factory.Factory):
    FACTORY_FOR = User
    first_name = 'John'
    last_name = 'Doe'
    #username = 'johndoe'
    username = factory.Sequence(lambda n: 'User ' + n)
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


class DBA_Factory(factory.Factory):
    FACTORY_FOR = User
    first_name = 'Bill'
    last_name = 'Gates'
    #username = 'billgates'
    username = factory.Sequence(lambda n: 'DBA' + n)
    email = 'microsoft@sucks.com'    
    is_superuser = True


class ManagerFactory(factory.Factory):
    FACTORY_FOR = User
    first_name = 'Boss'
    last_name = 'Hogg'
    username = 'bosshogg'
    email = 'bosshogg@hotmail.com'    
    manager = True

class LakeFactory(factory.Factory):
    FACTORY_FOR = Lake
    lake = "Lake Huron"

class EmployeeFactory(factory.Factory):
    FACTORY_FOR = Employee
    user = factory.SubFactory(UserFactory)
    position = 'worker bee'
    role = 'employee'
    #lake = factory.SubFactory(LakeFactory)
    supervisor = None

class ProjTypeFactory(factory.Factory):
    FACTORY_FOR = ProjectType
    project_type = "Offshore Index"

class DatabaseFactory(factory.Factory):
    FACTORY_FOR = Database
    master_database = "Offshore Master"
    Path = "C:/Path/to/somedb.mdb"    


class FamilyFactory(factory.Factory):
    FACTORY_FOR = Family
    id = factory.Sequence(lambda n:n)

    
class ProjectFactory(factory.Factory):
    '''year and slug are built by the project save method'''
    FACTORY_FOR = Project
    PRJ_CD = "LHA_IA12_123"
    #slug = "lha_ia12_123"
    #slug = factory.LazyAttribute(lambda a:slugify(a.PRJ_CD))
    PRJ_NM = "Fake Project"
    PRJ_LDR = "Bob Sakamano"
    #PRJ_DATE0 = datetime.strptime("January 15, 20%s" 
    #                                % PRJ_CD[6:8], "%B %d, %Y")
    #PRJ_DATE1 = datetime.strptime("May 15, 20%s" % PRJ_CD[6:8], "%B %d, %Y")
    #year = factory.LazyAttribute(lambda a:a.PRJ_DATE1.year)
    #Approved = True
    COMMENT = "This is a fake project"
    project_type = factory.SubFactory(ProjTypeFactory)
    master_database = factory.SubFactory(DatabaseFactory)
    Owner = factory.SubFactory(UserFactory)
    DBA = factory.SubFactory(DBA_Factory)

    Lake = factory.SubFactory(LakeFactory)


    @factory.lazy_attribute
    def PRJ_DATE0(a):
        datestring = "January 15, 20%s" % a.PRJ_CD[6:8] 
        PRJ_DATE0 = datetime.datetime.strptime(datestring, "%B %d, %Y")
        return(PRJ_DATE0)

    @factory.lazy_attribute
    def PRJ_DATE1(a):
        datestring = "January 15, 20%s" % a.PRJ_CD[6:8] 
        PRJ_DATE1 = datetime.datetime.strptime(datestring, "%B %d, %Y")
        return(PRJ_DATE1)

class ProjectSisters(factory.Factory):
    FACTORY_FOR = ProjectSisters    
    family = factory.SubFactory(FamilyFactory)
    project = factory.SubFactory(ProjectFactory)

class MilestoneFactory(factory.Factory):
    FACTORY_FOR = Milestone
    '''Look-up table of reporting milestone'''
    label = "Completion Report"
    category = "Core"
    order = 1

class ProjectMilestonesFactory(factory.Factory):
    FACTORY_FOR = ProjectMilestones
    '''list of reporting requirements for each project'''
    project = factory.SubFactory(ProjectFactory)
    milestone = factory.SubFactory(MilestoneFactory)

class ReportFactory(factory.Factory):
    FACTORY_FOR = Report
    current = True
    #projectreport = factory.SubFactory(ProjectMilestonesFactory)
    report_path = "some/fake/file.txt"
    uploaded_by = "Bob"
    report_hash = "1234"

    
