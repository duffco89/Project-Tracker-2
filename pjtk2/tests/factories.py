import factory
from datetime import datetime
from django.contrib.auth.models import User

from pjtk2.models import Project, TL_ProjType, TL_Database


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
    #PRJ_DATE0 = "January 15, 2012"
    #PRJ_DATE1 = "May 15, 2012"
    COMMENT = "This is a fake project"
    ProjectType = factory.SubFactory(ProjTypeFactory)
    MasterDatabase = factory.SubFactory(DatabaseFactory)
    Owner = factory.SubFactory(UserFactory)

