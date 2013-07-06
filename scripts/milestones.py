#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file has been automatically generated.
# Instead of changing it, create a file called import_helper.py
# which this script has hooks to.
#
# On that file, don't forget to add the necessary Django imports
# and take a look at how locate_object() and save_or_locate()
# are implemented here and expected to behave.
#
# This file was generated with the following command:
# manage.py dumpscript pjtk2.Milestone
#
# to restore it, run
# manage.py runscript module_name.this_script_name
#
# example: if manage.py is at ./manage.py
# and the script is at ./some_folder/some_script.py
# you must make sure ./some_folder/__init__.py exists
# and run  ./manage.py runscript some_folder.some_script


IMPORT_HELPER_AVAILABLE = False
try:
    import import_helper
    IMPORT_HELPER_AVAILABLE = True
except ImportError:
    pass

import datetime
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType

def run():
    #initial imports

    def locate_object(original_class, original_pk_name, the_class, pk_name, pk_value, obj_content):
        #You may change this function to do specific lookup for specific objects
        #
        #original_class class of the django orm's object that needs to be located
        #original_pk_name the primary key of original_class
        #the_class      parent class of original_class which contains obj_content
        #pk_name        the primary key of original_class
        #pk_value       value of the primary_key
        #obj_content    content of the object which was not exported.
        #
        #you should use obj_content to locate the object on the target db
        #
        #and example where original_class and the_class are different is
        #when original_class is Farmer and
        #the_class is Person. The table may refer to a Farmer but you will actually
        #need to locate Person in order to instantiate that Farmer
        #
        #example:
        #if the_class == SurveyResultFormat or the_class == SurveyType or the_class == SurveyState:
        #    pk_name="name"
        #    pk_value=obj_content[pk_name]
        #if the_class == StaffGroup:
        #    pk_value=8


        if IMPORT_HELPER_AVAILABLE and hasattr(import_helper, "locate_object"):
            return import_helper.locate_object(original_class, original_pk_name, the_class, pk_name, pk_value, obj_content)

        search_data = { pk_name: pk_value }
        the_obj =the_class.objects.get(**search_data)
        return the_obj

    def save_or_locate(the_obj):
        if IMPORT_HELPER_AVAILABLE and hasattr(import_helper, "save_or_locate"):
            the_obj = import_helper.save_or_locate(the_obj)
        else:
            the_obj.save()
        return the_obj



    #Processing model: Milestone

    from pjtk2.models import Milestone

    pjtk2_milestone_1 = Milestone()
    pjtk2_milestone_1.label = u'Project Proposal'
    pjtk2_milestone_1.category = u'Core'
    pjtk2_milestone_1.report = True
    pjtk2_milestone_1.protected = False
    pjtk2_milestone_1.order = 1
    pjtk2_milestone_1 = save_or_locate(pjtk2_milestone_1)

    pjtk2_milestone_2 = Milestone()
    pjtk2_milestone_2.label = u'Project Proposal Presentation'
    pjtk2_milestone_2.category = u'Core'
    pjtk2_milestone_2.report = True
    pjtk2_milestone_2.protected = False
    pjtk2_milestone_2.order = 2
    pjtk2_milestone_2 = save_or_locate(pjtk2_milestone_2)

    pjtk2_milestone_3 = Milestone()
    pjtk2_milestone_3.label = u'Field Protocol'
    pjtk2_milestone_3.category = u'Core'
    pjtk2_milestone_3.report = True
    pjtk2_milestone_3.protected = False
    pjtk2_milestone_3.order = 3
    pjtk2_milestone_3 = save_or_locate(pjtk2_milestone_3)

    pjtk2_milestone_4 = Milestone()
    pjtk2_milestone_4.label = u'Project Completion Report'
    pjtk2_milestone_4.category = u'Core'
    pjtk2_milestone_4.report = True
    pjtk2_milestone_4.protected = False
    pjtk2_milestone_4.order = 4
    pjtk2_milestone_4 = save_or_locate(pjtk2_milestone_4)

    pjtk2_milestone_5 = Milestone()
    pjtk2_milestone_5.label = u'Project Completion Pres.'
    pjtk2_milestone_5.category = u'Core'
    pjtk2_milestone_5.report = True
    pjtk2_milestone_5.protected = False
    pjtk2_milestone_5.order = 5
    pjtk2_milestone_5 = save_or_locate(pjtk2_milestone_5)

    pjtk2_milestone_6 = Milestone()
    pjtk2_milestone_6.label = u'Summary Report'
    pjtk2_milestone_6.category = u'Core'
    pjtk2_milestone_6.report = True
    pjtk2_milestone_6.protected = False
    pjtk2_milestone_6.order = 7
    pjtk2_milestone_6 = save_or_locate(pjtk2_milestone_6)

    pjtk2_milestone_7 = Milestone()
    pjtk2_milestone_7.label = u'Budget Report'
    pjtk2_milestone_7.category = u'Custom'
    pjtk2_milestone_7.report = True
    pjtk2_milestone_7.protected = False
    pjtk2_milestone_7.order = 99
    pjtk2_milestone_7 = save_or_locate(pjtk2_milestone_7)

    pjtk2_milestone_8 = Milestone()
    pjtk2_milestone_8.label = u'Approved'
    pjtk2_milestone_8.category = u'Core'
    pjtk2_milestone_8.report = False
    pjtk2_milestone_8.protected = True
    pjtk2_milestone_8.order = 2
    pjtk2_milestone_8 = save_or_locate(pjtk2_milestone_8)

    pjtk2_milestone_9 = Milestone()
    pjtk2_milestone_9.label = u'Submitted'
    pjtk2_milestone_9.category = u'Core'
    pjtk2_milestone_9.report = False
    pjtk2_milestone_9.protected = False
    pjtk2_milestone_9.order = 1
    pjtk2_milestone_9 = save_or_locate(pjtk2_milestone_9)

    pjtk2_milestone_10 = Milestone()
    pjtk2_milestone_10.label = u'Field Work Conducted'
    pjtk2_milestone_10.category = u'Core'
    pjtk2_milestone_10.report = False
    pjtk2_milestone_10.protected = True
    pjtk2_milestone_10.order = 3
    pjtk2_milestone_10 = save_or_locate(pjtk2_milestone_10)

    pjtk2_milestone_11 = Milestone()
    pjtk2_milestone_11.label = u'Data Scrubbed'
    pjtk2_milestone_11.category = u'Core'
    pjtk2_milestone_11.report = False
    pjtk2_milestone_11.protected = False
    pjtk2_milestone_11.order = 4
    pjtk2_milestone_11 = save_or_locate(pjtk2_milestone_11)

    pjtk2_milestone_12 = Milestone()
    pjtk2_milestone_12.label = u'Aging Complete'
    pjtk2_milestone_12.category = u'Core'
    pjtk2_milestone_12.report = False
    pjtk2_milestone_12.protected = False
    pjtk2_milestone_12.order = 5
    pjtk2_milestone_12 = save_or_locate(pjtk2_milestone_12)

    pjtk2_milestone_13 = Milestone()
    pjtk2_milestone_13.label = u'Data Merged'
    pjtk2_milestone_13.category = u'Core'
    pjtk2_milestone_13.report = False
    pjtk2_milestone_13.protected = True
    pjtk2_milestone_13.order = 6
    pjtk2_milestone_13 = save_or_locate(pjtk2_milestone_13)

    pjtk2_milestone_14 = Milestone()
    pjtk2_milestone_14.label = u'Sign off'
    pjtk2_milestone_14.category = u'Core'
    pjtk2_milestone_14.report = False
    pjtk2_milestone_14.protected = True
    pjtk2_milestone_14.order = 200
    pjtk2_milestone_14 = save_or_locate(pjtk2_milestone_14)

    pjtk2_milestone_15 = Milestone()
    pjtk2_milestone_15.label = u'Stomach Analysis'
    pjtk2_milestone_15.category = u'Custom'
    pjtk2_milestone_15.protected = False
    pjtk2_milestone_15.report = False
    pjtk2_milestone_15.order = 99
    pjtk2_milestone_15 = save_or_locate(pjtk2_milestone_15)

