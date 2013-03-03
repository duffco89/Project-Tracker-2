import factory
from datetime import datetime
from django.contrib.auth.models import User

from pjtk2.models import *



class UserFactory(factory.Factory):
    FACTORY_FOR = User
    first_name = 'John'
    last_name = 'Doe'
    username = 'johndoe'
    email = 'johndoe@hotmail.com'    
    #admin = False

class ProjTypeFactory(factory.Factory):
    FACTORY_FOR = TL_ProjType
    Project_Type = "Offshore Index"

class DatabaseFactory(factory.Factory):
    FACTORY_FOR = TL_Database
    MasterDatabase = "Offshore Master"
    Path = "C:/Path/to/somedb.mdb"    
    
class ProjectFactory(factory.Factory):
    FACTORY_FOR = Project
    PRJ_CD = "LHA_IA12_123"
    PRJ_NM = "Fake Project"
    PRJ_LDR = "Bob Sakamano"
    PRJ_DATE0 = datetime.strptime("January 15, 2012", "%B %d, %Y")
    PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y")
    COMMENT = "This is a fake project"
    ProjectType = factory.SubFactory(ProjTypeFactory)
    MasterDatabase = factory.SubFactory(DatabaseFactory)
    Owner = factory.SubFactory(UserFactory)


class MilestoneFactory(factory.Factory):
    FACTORY_FOR = Milestone
    '''Look-up table of reporting milestone'''
    label = "Completion Report"
    category = "core"
    order = 1

class ProjectReportsFactory(factory.Factory):
    FACTORY_FOR = ProjectReports
    '''list of reporting requirements for each project'''
    project = factory.SubFactory(ProjectFactory)
    report_type = factory.SubFactory(MilestoneFactory)

class ReportFactory(factory.Factory):
    FACTORY_FOR = Report
    current = True
    projectreport = factory.SubFactory(ProjectReportsFactory)
    report_path = "some/fake/file.txt"
    uploaded_by = "Bob"
    report_hash = "1234"

    
