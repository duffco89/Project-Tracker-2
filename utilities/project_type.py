#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file has been automatically generated.
# Instead of changing it, create a file called import_helper.py
# and put there a class called ImportHelper(object) in it.
#
# This class will be specially casted so that instead of extending object,
# it will actually extend the class BasicImportHelper()
#
# That means you just have to overload the methods you want to
# change, leaving the other ones inteact.
#
# Something that you might want to do is use transactions, for example.
#
# Also, don't forget to add the necessary Django imports.
#
# This file was generated with the following command:
# manage.py dumpscript pjtk2.ProjectType
#
# to restore it, run
# manage.py runscript module_name.this_script_name
#
# example: if manage.py is at ./manage.py
# and the script is at ./some_folder/some_script.py
# you must make sure ./some_folder/__init__.py exists
# and run  ./manage.py runscript some_folder.some_script

# usage:
#  python manage.py runscript proj_type



from django.db import transaction

class BasicImportHelper(object):

    def pre_import(self):
        pass

    # You probably want to uncomment on of these two lines
    # @transaction.atomic  # Django 1.6
    # @transaction.commit_on_success  # Django <1.6
    def run_import(self, import_data):
        import_data()

    def post_import(self):
        pass

    def locate_similar(self, current_object, search_data):
        #you will probably want to call this method from save_or_locate()
        #example:
        #new_obj = self.locate_similar(the_obj, {"national_id": the_obj.national_id } )

        the_obj = current_object.__class__.objects.get(**search_data)
        return the_obj

    def locate_object(self, original_class, original_pk_name, the_class, pk_name, pk_value, obj_content):
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

        search_data = { pk_name: pk_value }
        the_obj = the_class.objects.get(**search_data)
        #print(the_obj)
        return the_obj


    def save_or_locate(self, the_obj):
        #change this if you want to locate the object in the database
        try:
            the_obj.save()
        except:
            print("---------------")
            print("Error saving the following object:")
            print(the_obj.__class__)
            print(" ")
            print(the_obj.__dict__)
            print(" ")
            print(the_obj)
            print(" ")
            print("---------------")

            raise
        return the_obj


importer = None
try:
    import import_helper
    #we need this so ImportHelper can extend BasicImportHelper, although import_helper.py
    #has no knowlodge of this class
    importer = type("DynamicImportHelper", (import_helper.ImportHelper, BasicImportHelper ) , {} )()
except ImportError as e:
    if str(e) == "No module named import_helper":
        importer = BasicImportHelper()
    else:
        raise

import datetime
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType

def run():
    importer.pre_import()
    importer.run_import(import_data)
    importer.post_import()

def import_data():
    #initial imports

    #Processing model: ProjectType

    from pjtk2.models import ProjectType

    pjtk2_projecttype_1 = ProjectType()
    pjtk2_projecttype_1.project_type = u'Aging QAQC'
    pjtk2_projecttype_1 = importer.save_or_locate(pjtk2_projecttype_1)

    pjtk2_projecttype_2 = ProjectType()
    pjtk2_projecttype_2.project_type = u'Benthic Sampling'
    pjtk2_projecttype_2 = importer.save_or_locate(pjtk2_projecttype_2)

    pjtk2_projecttype_3 = ProjectType()
    pjtk2_projecttype_3.project_type = u'Brood stock'
    pjtk2_projecttype_3 = importer.save_or_locate(pjtk2_projecttype_3)

    pjtk2_projecttype_4 = ProjectType()
    pjtk2_projecttype_4.project_type = u'Commercial Catch Sampling'
    pjtk2_projecttype_4 = importer.save_or_locate(pjtk2_projecttype_4)

    pjtk2_projecttype_5 = ProjectType()
    pjtk2_projecttype_5.project_type = u'Commerical Harvest and Stock Status Reporting'
    pjtk2_projecttype_5 = importer.save_or_locate(pjtk2_projecttype_5)

    pjtk2_projecttype_6 = ProjectType()
    pjtk2_projecttype_6.project_type = u'Creel Survey'
    pjtk2_projecttype_6 = importer.save_or_locate(pjtk2_projecttype_6)

    pjtk2_projecttype_7 = ProjectType()
    pjtk2_projecttype_7.project_type = u'CWT Recovery and Analysis'
    pjtk2_projecttype_7 = importer.save_or_locate(pjtk2_projecttype_7)

    pjtk2_projecttype_8 = ProjectType()
    pjtk2_projecttype_8.project_type = u'Derby Monitoring'
    pjtk2_projecttype_8 = importer.save_or_locate(pjtk2_projecttype_8)

    pjtk2_projecttype_9 = ProjectType()
    pjtk2_projecttype_9.project_type = u'Diet Analysis'
    pjtk2_projecttype_9 = importer.save_or_locate(pjtk2_projecttype_9)

    pjtk2_projecttype_10 = ProjectType()
    pjtk2_projecttype_10.project_type = u'End of Spring Trap Netting (ESTN)'
    pjtk2_projecttype_10 = importer.save_or_locate(pjtk2_projecttype_10)

    pjtk2_projecttype_11 = ProjectType()
    pjtk2_projecttype_11.project_type = u'Fall Lake Trout Index Netting (FLIN)'
    pjtk2_projecttype_11 = importer.save_or_locate(pjtk2_projecttype_11)

    pjtk2_projecttype_12 = ProjectType()
    pjtk2_projecttype_12.project_type = u'Fall Lake Trout Spawning Survey'
    pjtk2_projecttype_12 = importer.save_or_locate(pjtk2_projecttype_12)

    pjtk2_projecttype_13 = ProjectType()
    pjtk2_projecttype_13.project_type = u'Fall Preyfish Hydroacoustic Survey'
    pjtk2_projecttype_13 = importer.save_or_locate(pjtk2_projecttype_13)

    pjtk2_projecttype_14 = ProjectType()
    pjtk2_projecttype_14.project_type = u'Fall Trap Net'
    pjtk2_projecttype_14 = importer.save_or_locate(pjtk2_projecttype_14)

    pjtk2_projecttype_15 = ProjectType()
    pjtk2_projecttype_15.project_type = u'Fall Walleye Index Netting (FWIN)'
    pjtk2_projecttype_15 = importer.save_or_locate(pjtk2_projecttype_15)

    pjtk2_projecttype_16 = ProjectType()
    pjtk2_projecttype_16.project_type = u'Fall Whitefish Spawning Survey'
    pjtk2_projecttype_16 = importer.save_or_locate(pjtk2_projecttype_16)

    pjtk2_projecttype_17 = ProjectType()
    pjtk2_projecttype_17.project_type = u'Fish Stocking'
    pjtk2_projecttype_17 = importer.save_or_locate(pjtk2_projecttype_17)

    pjtk2_projecttype_18 = ProjectType()
    pjtk2_projecttype_18.project_type = u'Fishway Monitoring'
    pjtk2_projecttype_18 = importer.save_or_locate(pjtk2_projecttype_18)

    pjtk2_projecttype_19 = ProjectType()
    pjtk2_projecttype_19.project_type = u'Lamprey Monitoring and Reporting'
    pjtk2_projecttype_19 = importer.save_or_locate(pjtk2_projecttype_19)

    pjtk2_projecttype_20 = ProjectType()
    pjtk2_projecttype_20.project_type = u'Nearshore Community Index Netting (NSCIN)'
    pjtk2_projecttype_20 = importer.save_or_locate(pjtk2_projecttype_20)

    pjtk2_projecttype_21 = ProjectType()
    pjtk2_projecttype_21.project_type = u'Nearshore Index Netting'
    pjtk2_projecttype_21 = importer.save_or_locate(pjtk2_projecttype_21)

    pjtk2_projecttype_22 = ProjectType()
    pjtk2_projecttype_22.project_type = u'Offshore Index Netting'
    pjtk2_projecttype_22 = importer.save_or_locate(pjtk2_projecttype_22)

    pjtk2_projecttype_23 = ProjectType()
    pjtk2_projecttype_23.project_type = u'Small Fish Assessment'
    pjtk2_projecttype_23 = importer.save_or_locate(pjtk2_projecttype_23)

    pjtk2_projecttype_24 = ProjectType()
    pjtk2_projecttype_24.project_type = u'Sportfish Monitoring or Collections'
    pjtk2_projecttype_24 = importer.save_or_locate(pjtk2_projecttype_24)

    pjtk2_projecttype_25 = ProjectType()
    pjtk2_projecttype_25.project_type = u'Spring Muskellunge Index Netting (SMIN)'
    pjtk2_projecttype_25 = importer.save_or_locate(pjtk2_projecttype_25)

    pjtk2_projecttype_26 = ProjectType()
    pjtk2_projecttype_26.project_type = u'Spring Walleye Index Netting (SWIN)'
    pjtk2_projecttype_26 = importer.save_or_locate(pjtk2_projecttype_26)

    pjtk2_projecttype_27 = ProjectType()
    pjtk2_projecttype_27.project_type = u'Sturgeon Spawning Assessment'
    pjtk2_projecttype_27 = importer.save_or_locate(pjtk2_projecttype_27)

