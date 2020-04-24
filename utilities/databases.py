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
# manage.py dumpscript pjtk2.Database
#
# to restore it, run
# manage.py runscript module_name.this_script_name
#
# example: if manage.py is at ./manage.py
# and the script is at ./some_folder/some_script.py
# you must make sure ./some_folder/__init__.py exists
# and run  ./manage.py runscript some_folder.some_script

# usage:
#  python manage.py runscript databases



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

    #Processing model: Database

    from pjtk2.models import Database

    pjtk2_database_1 = Database()
    pjtk2_database_1.master_database = u'Benthic Master'
    pjtk2_database_1.path = u'Z:\\Data Warehouse\\Derived Datasets\\UNIT PROJECTS\\Benthics\\Lake Huron Benthics.mdb'
    pjtk2_database_1 = importer.save_or_locate(pjtk2_database_1)

    pjtk2_database_2 = Database()
    pjtk2_database_2.master_database = u'Commercial Catch Sampling Master (CF)'
    pjtk2_database_2.path = u'Z:\\Data Warehouse\\Commercial Fisheries\\Catch Sampling\\CF_Master.mdb'
    pjtk2_database_2 = importer.save_or_locate(pjtk2_database_2)

    pjtk2_database_3 = Database()
    pjtk2_database_3.master_database = u'Commercial Harvest Master (CH)'
    pjtk2_database_3.path = u'Z:\\Data Warehouse\\Commercial Fisheries\\Harvest and Effort\\CH_MASTER.mdb'
    pjtk2_database_3 = importer.save_or_locate(pjtk2_database_3)

    pjtk2_database_4 = Database()
    pjtk2_database_4.master_database = u'Creel Master'
    pjtk2_database_4.path = u'Z:\\Data Warehouse\\Recreational Fisheries\\Creel\\SC\\SC_Master.mdb'
    pjtk2_database_4 = importer.save_or_locate(pjtk2_database_4)

    pjtk2_database_5 = Database()
    pjtk2_database_5.master_database = u'Fish Stocking  Master (FS)'
    pjtk2_database_5.path = u'Y:\\Information Resources\\Dataset_Utilities\\FS_Maker\\FS_Master.mdb'
    pjtk2_database_5 = importer.save_or_locate(pjtk2_database_5)

    pjtk2_database_6 = Database()
    pjtk2_database_6.master_database = u'Fishway Master'
    pjtk2_database_6.path = u'Z:\\Data Warehouse\\Assessment\\Fishway\\Fishway_Master.mdb'
    pjtk2_database_6 = importer.save_or_locate(pjtk2_database_6)

    pjtk2_database_7 = Database()
    pjtk2_database_7.master_database = u'Nearshore Master'
    pjtk2_database_7.path = u'Z:\\Data Warehouse\\Assessment\\Index\\Nearshore\\IA_NEARSHORE.mdb'
    pjtk2_database_7 = importer.save_or_locate(pjtk2_database_7)

    pjtk2_database_8 = Database()
    pjtk2_database_8.master_database = u'Offshore Master'
    pjtk2_database_8.path = u'Z:\\Data Warehouse\\Assessment\\Index\\Offshore\\IA_OFFSHORE.mdb'
    pjtk2_database_8 = importer.save_or_locate(pjtk2_database_8)

    pjtk2_database_9 = Database()
    pjtk2_database_9.master_database = u'Small Fish Master'
    pjtk2_database_9.path = u'Z:\\Data Warehouse\\Assessment\\Index\\Nearshore\\Small_Fish\\COA_Nearshore_Smallfish.mdb'
    pjtk2_database_9 = importer.save_or_locate(pjtk2_database_9)

    pjtk2_database_10 = Database()
    pjtk2_database_10.master_database = u'Sportfish Master (SF)'
    pjtk2_database_10.path = u'Z:\\Data Warehouse\\Recreational Fisheries\\Angler Diary\\Sf\\SF_MASTER.mdb'
    pjtk2_database_10 = importer.save_or_locate(pjtk2_database_10)

    pjtk2_database_11 = Database()
    pjtk2_database_11.master_database = u'Stomach Master'
    pjtk2_database_11.path = u'Z:\\Data Warehouse\\Assessment\\Diets\\Stomach Analysis\\Stomach_Master.mdb'
    pjtk2_database_11 = importer.save_or_locate(pjtk2_database_11)

    pjtk2_database_12 = Database()
    pjtk2_database_12.master_database = u'Sturgeon Master'
    pjtk2_database_12.path = u'Z:\\Data Warehouse\\Derived Datasets\\UNIT PROJECTS\\Sturgeon\\Sturgeon Master.mdb'
    pjtk2_database_12 = importer.save_or_locate(pjtk2_database_12)

    pjtk2_database_13 = Database()
    pjtk2_database_13.master_database = u'Not Applicable'
    pjtk2_database_13.path = u'path/to/nowhere'
    pjtk2_database_13 = importer.save_or_locate(pjtk2_database_13)

