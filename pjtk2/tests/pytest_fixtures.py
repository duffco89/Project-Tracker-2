'''
=============================================================
/home/adam/Documents/djcode/pjtk2/pjtk2/tests/pytest_fixtures.py
Created: 30 Apr 2014 17:38:30


DESCRIPTION:



A. Cottrill
=============================================================
'''
from django.contrib.auth.models import Group
import pytest
from .factories import *

@pytest.fixture(scope="module", autouse=True)
def disconnect_signals():
    '''disconnect the signals before each test - not needed here'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)


@pytest.fixture(scope='module')
def user(db):
    """return a normal user named homer
    """
    password = "Abcd1234"
    homer = UserFactory.create(username = 'hsimpson',
                        first_name = 'Homer',
                        last_name = 'Simpson',
                        password = password)
    return(homer)


@pytest.fixture(scope='module')
def joe_user(db):
    """return a normal user named joe blow
    """
    password = "Abcd1234"
    joe = UserFactory.create(username = 'jblow',
                        first_name = 'Joe',
                        last_name = 'Blow',
                        password = password)
    return(joe)


@pytest.fixture(scope='module')
def dba(db):
    """return a normal user named homer
    """
    password = "Abcd1234"
    kramer = DBA_Factory.create(username = 'ckramer',
                        first_name = 'cozmo',
                        last_name = 'kramer',
                        password = password)
    return(kramer)


@pytest.fixture(scope='module')
def manager(db):
    """return a manager user named monty
    """
    password = "Abcd1234"
    monty = UserFactory.create(username = 'mburns',
                        first_name = 'monty',
                        last_name = 'burns',
                        password = password)
    #make Mr. Burns the manager:
    managerGrp, created = Group.objects.get_or_create(name='manager')
    monty.groups.add(managerGrp)

    return(monty)


@pytest.fixture(scope='module')
def project(db, user):
    '''create a simple project with basic approved and signoff milestones'''

    milestone1 = MilestoneFactory.create(label = "Approved")
    milestone2 = MilestoneFactory.create(label = "Sign Off")

    project = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                          owner=user)
    return(project)
