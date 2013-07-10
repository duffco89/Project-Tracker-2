
# E1101 - Class 'whatever' has no 'something' member
# E1120 - No value passed for parameter 'cls' in function call
#pylint: disable=E1101, E1120

from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
#from django.db.models.signals import pre_save, post_save
#from django.dispatch import receiver
from django.template.defaultfilters import slugify

from taggit.managers import TaggableManager

import datetime
import pytz
import pdb


class ProjectsManager(models.Manager):
    '''two custom extensions to the base manager for project objects to
    return approved and completed projects.'''


    def submitted(self):
        '''return a queryset containing only those projects that have been
        submitted, but have not yet been approved or completed.
        '''
        return self.filter(active=True,
                           projectmilestones__milestone__label='Approved',
                           projectmilestones__completed__isnull=True).filter(
                           projectmilestones__milestone__label='Sign off',
                           projectmilestones__completed__isnull=True)

    def approved(self):
        '''return a queryset containing only those projects that have been
        approved, but have not been completed.
        '''
        return self.filter(active=True,
                           projectmilestones__milestone__label='Approved',
                           projectmilestones__completed__isnull=False).filter(
                           projectmilestones__milestone__label='Sign off',
                   projectmilestones__completed__isnull=True)

    def completed(self):
        '''return a queryset containing only those projects that have been
        both approved and completed.
        '''
        return self.filter(active=True,
                           projectmilestones__milestone__label='Approved',
                           projectmilestones__completed__isnull=False).filter(
                           projectmilestones__milestone__label='Sign off',
                           projectmilestones__completed__isnull=False)


class ProjectsThisYear(models.Manager):
    '''get all of the project objects from the current year'''
    def get_query_set(self):
        #use_for_related_fields = True
        year = datetime.datetime.now().year
        return super(ProjectsThisYear, self).get_query_set().filter(
                     year__gte=year, active=True)

class ProjectsLastYear(models.Manager):
    '''get all of the project objects from last year'''
    def get_query_set(self):
        #use_for_related_fields = True
        year = datetime.datetime.now().year - 1
        return super(ProjectsLastYear, self).get_query_set().filter(
                    year = year, active=True)


class MilestoneManager(models.Manager):
    '''Sumbitted milestone is created automatically when a project is
    created, and is needed for messages, but is not used anywhere else.
    This manager will auto-matically remove it from the returned
    recordsets.
    '''
    def get_query_set(self):
        use_for_related_fields = True
        return super(MilestoneManager, self).get_query_set().exclude(
                     label='Submitted')



class Milestone(models.Model):
    '''Look-up table of reporting milestone and their attributes.  Not all
    milestones will have a report associated with them.  Keeping
    milesstones in a separate tamles allows us to dynamically add and
    remove milesstones associated with individual projects or project
    types (field projects vs synthesis projects).
    protected is used to limit who can update various milestones.
    '''

    #(database, display)
    MILESTONE_CHOICES = {
        ('Core', 'core'),
        ('Suggested', 'suggested'),    
        ('Custom', 'custom'),
    }

    label = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=30, choices=MILESTONE_CHOICES,
                                default='Custom')
    report  = models.BooleanField(default = False)
    protected  = models.BooleanField(default = False)
    order = models.FloatField(default=99)

    objects = MilestoneManager()

    class Meta:
        verbose_name = "Milestones List"
        verbose_name_plural = "Milestones List"
        ordering = ['-report', 'order']

    def __unicode__(self):
        return self.label


class ProjectType(models.Model):
    '''A look-up table to hold project types'''
    project_type = models.CharField(max_length=150)
    
    class Meta:
        verbose_name = "Project Type"
    
    def __unicode__(self):
        '''return the project type  as its string representation'''
        return self.project_type


class Database(models.Model):
    '''A lookup table to hole list of master databases.'''
    master_database = models.CharField(max_length=250)
    path = models.CharField(max_length=250)

    class Meta:
        verbose_name = "Master Database"
    
    def __unicode__(self):
        '''return the database name as its string representation'''
        return self.master_database


class Lake(models.Model):
    '''A lookup table to hold the names of the different lakes'''
    lake = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Lake"
    
    def __unicode__(self):
        '''return the lake name as its string representation'''
        return self.lake

class Project(models.Model):
    '''Class to hold a record for each project
    '''

    #(database, display)
    FUNDING_CHOICES = {
        ('spa', 'SPA'),
        ('coa', 'COA'),    
        ('other', 'other'),
    }

    active  = models.BooleanField(default = True)
    year = models.CharField("Year", max_length=4, blank=True, editable=False)
    prj_date0 = models.DateField("Start Date", blank=False)
    prj_date1 = models.DateField("End Date", blank=False)
    PRJ_CD = models.CharField("Project Code", max_length=12, unique=True, 
                              blank=False)
    PRJ_NM = models.CharField("Proejct Name", max_length=50, blank=False)
    prj_ldr = models.CharField("Project Lead", max_length=40, blank=False)
    comment = models.TextField(blank=False, 
                               help_text="General project description.")
    help_str = "Potential risks associated with not running project."
    risk = models.TextField("Risk", null=True, blank=True, 
                            help_text=help_str)
    master_database = models.ForeignKey("Database", null=True, blank=True)
    project_type = models.ForeignKey("ProjectType", null=True, blank=True)

    field_project = models.BooleanField(default = True)
    owner = models.ForeignKey(User, blank=True, related_name="ProjectOwner")
    dba = models.ForeignKey(User, blank=True, related_name="ProjectDBA")
    funding = models.CharField("Funding Source", max_length=30, 
                               choices=FUNDING_CHOICES, default="spa")

    lake = models.ForeignKey(Lake, default=1)

    total_cost =  models.DecimalField("Total Cost", max_digits=8, 
                                     decimal_places=2, null=True, blank=True)

    slug = models.SlugField(blank=True, editable=False)
    tags = TaggableManager()

    #managers
    #objects = models.Manager()
    objects = ProjectsManager()
    last_year = ProjectsLastYear()
    this_year = ProjectsThisYear()


    class Meta:
        verbose_name = "Project List"
        ordering = ['-prj_date1']

    def approve(self):
        '''a helper method to make approving projects easier.  A
        project-milestone object will be created if it doesn't
        exist.
        '''
        now = datetime.datetime.now(pytz.utc)
        try:
            ProjectMilestones.objects.filter(project=self, 
                                     milestone__label='Approved').update(
                                         completed=now)
        except ProjectMilestones.DoesNotExist:
            #create it if it doesn't exist
            milestone = Milestone.objects.get(label='Approved')
            projectmilestone = ProjectMilestones(project=self, 
                                 milestone=milestone,
                                 required=True,
                                 completed=now)

    def unapprove(self):
        '''a helper method to reverse project.approved(), a project-milestone
        object will be created if it doesn't exist.'''
        try:
            ProjectMilestones.objects.filter(project=self, 
                                 milestone__label='Approved').update(
                                     completed=None)
        except ProjectMilestones.DoesNotExist:
            pass


    def is_approved(self):
        '''Is the current project approved?  Returns true if it is, otherwize
        false.'''
        approved = ProjectMilestones.objects.get(project=self, 
                                 milestone__label='Approved')
        if approved.completed != None:
            return(True)
        else:
            return(False)

    def signoff(self):
        '''A helper function to make it easier to sign off a project'''
        #TODO - add logic here to make sure all previous requirements
        #have been met! - can't signoff on a project that wasn't
        #approved or compelted.
        now = datetime.datetime.now(pytz.utc)
        try:
            ProjectMilestones.objects.filter(project=self, 
                                     milestone__label='Sign off').update(
                                         completed=now)
        except ProjectMilestones.DoesNotExist:
            pass

    def project_suffix(self):
        '''return the prject suffix for the given project'''
        return self.PRJ_CD[-3:]

    def name(self):
        '''alias for PRJ_NM - maintains fishnetII name in model but works
         with django convention of obj.name.'''
        return self.PRJ_NM

    def description(self):
        '''alias for comment - maintains fishnetII comment in model but works
         with django convention of obj.description.'''
        return self.comment

    def __unicode__(self):
        '''Return the name of the project and it's project code'''
        ret = "%s (%s)" % (self.PRJ_NM, self.PRJ_CD)
        return ret

    def get_milestones(self, required=True):
        '''get all of the milestone events have been assigned to 
        this project - (these are just milestone events where report==False)'''
        if required == True:
            return ProjectMilestones.objects.filter(project=self,
                                        required=True, 
                                        milestone__report=False).order_by(
                                        'milestone__order')
        else:
            return ProjectMilestones.objects.filter(project=self,
                                        milestone__report=False).order_by(
                                        'milestone__order')

    def get_reporting_requirements(self):
        '''get all of the reports have been assigned to 
        this project - no distinction between core or custom reports'''
        return ProjectMilestones.objects.filter(project=self,
                                                milestone__report=True)

    def get_uploaded_reports(self):
        '''get all of the CURRENT reports that are associated with this
        project.  Non-current reports are not included in this
        recordset.
        '''
        #TODO Filter for report=True
        return Report.objects.filter(current=True, 
                                     projectreport__project=self)


    def get_core_assignments(self, all_reports=True):
        '''get all of the core reports have been assigned to this project, if
        all is true, all assignements are returned, if all_reports
        is False, only required assignments are returned.

        '''

        if all_reports == True:
            assignments = self.get_reporting_requirements().filter(
                milestone__category='Core', milestone__report=True)
        else:
            assignments = self.get_reporting_requirements().filter(
                milestone__category='Core', 
                milestone__report=True).filter(required=True) 
        return assignments

    def get_custom_assignments(self):
        '''get a list of any custom reports that have been assigned to
        this project'''
        return self.get_reporting_requirements().filter(
                      required=True, milestone__report=True).exclude(
                      milestone__category='Core')

    def get_complete(self):
        '''get the project reports that have uploaded reports
        associated with them.'''
        #TODO Filter for report=True
        return ProjectMilestones.objects.filter(project=self).filter(
            report__in=Report.objects.filter(current=True,
                                             projectreport__project=self))

    def get_outstanding(self):
        '''these are the required reports that have not been submitted yet'''
        #TODO Filter for report=True
        return ProjectMilestones.objects.filter(project=self, 
                                milestone__report=True).exclude(
                                report__in=Report.objects.filter(
                                projectreport__project=self))


    def get_milestone_dicts(self):
        '''return a dictionary of dictionaries containing elements of
        all milestones, core and custom reports as well as vectors indicating
        which ones have been assigned to this project.'''

        #TODO Filter for report=True

        #get a queryset of all reports we consider 'core'
        milestones = Milestone.objects.filter(report=False)
        corereports = Milestone.objects.filter(category='Core', report=True)
        customreports = Milestone.objects.filter(category='Custom', report=True)
    
        #we need to convert the querset to a tuple of tuples
        milestones = tuple([(x[0], x[1]) for x in milestones.values_list()])
        corereports = tuple([(x[0], x[1]) for x in corereports.values_list()])
        customreports = tuple([(x[0], x[1]) for x 
                               in customreports.values_list()])    
        
        #get the milestones currently assigned to this project, if not return a
        #dictionary with all reports assigned
        milestones_assigned = self.get_milestones()
        milestones_assigned = [x.milestone_id for x 
                               in list(milestones_assigned)]

        core_assigned = self.get_core_assignments()
        core_assigned = [x.milestone_id for x in list(core_assigned)]

        custom_assigned = self.get_custom_assignments()
        custom_assigned = [x.milestone_id for x in list(custom_assigned)]
 
        #put the reports and assigned reports in a dictionary    
        milestones = dict(milestones=milestones, assigned=milestones_assigned)
        core = dict(milestones=corereports, assigned=core_assigned)
        custom = dict(milestones=customreports, assigned=custom_assigned)

        milestones_dict = dict(Milestones=milestones, Core=core, Custom=custom)
    
        return milestones_dict


    def initialize_milestones(self):
        '''A function that will add a record into "ProjectMilestones" for
        each of the core reports and milestones for newly created projects'''

        #project = Project.objects.get(slug=slug)
        corereports = Milestone.objects.filter(category='Core')

        for report in corereports:
            #pr,created = ProjectMilestones.objects.get_or_create(project=self, 
            #                                            milestone = report)
            ProjectMilestones.objects.get_or_create(project=self, 
                                                        milestone = report)

    def get_family(self):   
        '''If this project belongs to a familiy (i.e. - has sisters) return
        the family, otherwise return None.'''

        try:
            family = Family.objects.get(projectsisters__project=self)
        except Family.DoesNotExist:
            family = None  
        return family

    def add_sister(self, slug):
        '''Add the project identified by slug to the familiy of the current
        project.  If the current project, doesn't belong to a family, create
        it first then add the sister.
        '''

        family = self.get_family()
        if family is None:
            family = Family.objects.create()
            ProjectSisters.objects.create(project=self, family=family)

        #now add the project associated with slug to family:
        project = Project.objects.get(slug=slug)
        ProjectSisters.objects.create(project=project, family=family)

    def get_sisters(self, excludeself = True):
        '''return a queryset of sister projects associated with this
        project. - By default, the current project is not incuded in
        the recordset'''
        family = self.get_family()
        if family:
            try:
                if excludeself:
                    sisters = Project.objects.filter(
                        projectsisters__family=family).exclude(slug=self.slug)
                else:
                    sisters = Project.objects.filter(
                        projectsisters__family=family)
            except Project.DoesNotExist:
                sisters = []
        else:
            sisters = []
        return sisters


    def get_sister_candidates(self):
        '''return a querset of projects that could be sisters to this
        project.  To be a candidates for sisterhood, a project must be
        approved, be the same project type, run in the same year and
        not be a sister to another project. If the current project
        isn't approved, no candidates will be returned regardless.'''
        if self.is_approved():
            try:
                candidates = Project.objects.approved().filter(
                                      project_type=self.project_type, 
                                      year = self.year,
                                      projectsisters__isnull=True).exclude(
                                      slug=self.slug)
            except Project.DoesNotExist:
                candidates = []
        else:
            candidates = []
        return candidates            

    def delete_sister(self, slug):
        '''remove the project identified by "slug" from the familiy associated
        with this project.  If this project is now the only member of
        teh familiy, delete the family so we don't end-up with a bunch
        of single member families.
        '''
        project = Project.objects.get(slug=slug)
        ProjectSisters.objects.filter(project=project).delete()
        family = self.get_family()
        #if this was the last sibling in the family get rid of its
        #record and the family record too.
        familysize = ProjectSisters.objects.filter(family=family).count()
        if familysize == 1:
            ProjectSisters.objects.filter(family=family).delete()
            Family.objects.filter(id=family.id).delete()                    


    def disown(self):
        '''the special case when we want to remove this project from an
        existing family, but keep the other sister relationships intact.'''

        family = self.get_family()

        self.delete_sister(self.slug)
        #if this was the last sibling in the family get rid of it too.
        familysize = ProjectSisters.objects.filter(family=family.id).count()
        if familysize == 1:
            ProjectSisters.objects.filter(family=family).delete()
            Family.objects.filter(id=family.id).delete()                    


    #@models.permalink
    def get_absolute_url(self):
        '''return the url for the project'''
        url = reverse('pjtk2.views.project_detail', kwargs={'slug':self.slug})
        return url

    def save(self, *args, **kwargs):
        """
        from:http://stackoverflow.com/questions/7971689/
             generate-slug-field-in-existing-table
        Slugify name if it doesn't exist. IMPORTANT: doesn't check to see
        if slug is a dupicate!
        """
        new = False
        if not self.slug or not self.year:
            self.slug = slugify(self.PRJ_CD)
            self.year = self.prj_date0.year
            new = True

        super(Project, self).save( *args, **kwargs)
        if new:
            self.initialize_milestones()


##  @receiver(post_save, sender=Project)
##  def send_notices_if_changed(sender, instance, created, **kwargs):
##      '''If this project was just created, we will need to send a
##      notification to the project lead and his/her supervisors, and the
##      data custodian that it was submitted.
##      '''
##  
##      if created:
##          proj = Project.objects.get(pk=instance.pk)
##          msgtxt =  "Project %s was just submitted." % proj.PRJ_CD
##          # we want to send this message up the chain of command to 
##          # all supervisors
##          try:
##              #try and send messages starting at project lead - ideal
##              prjLead = proj.prj_ldr
##              prjLead = Employee.objects.get(user__username=prjLead)
##              users = get_supervisors(prjLead)
##          except:
##              #should be the same person, but could be someone else
##              prjLead = proj.owner
##              prjLead = Employee.objects.get(user__username=prjLead)
##              users = get_supervisors(prjLead)
##          #send notice to dba too
##          users.append(Employee.objects.get(user__username=proj.dba))
##          #remove any duplicates
##          users = list(set(users))
##          ms = Milestone.objects.get(label="Submitted")
##          sendMessage(msgtxt, users, project=proj, milestone=ms)
##  
            
class ProjectMilestones(models.Model):
    '''list of reporting requirements for each project'''
    #aka - project milestones
    project = models.ForeignKey('Project')
    #report_type = models.ForeignKey('Milestone')
    milestone = models.ForeignKey('Milestone')
    required  = models.BooleanField(default=True)
    completed = models.DateTimeField(blank=True, null=True)

    class Meta:
        #unique_together = ("project", "report_type",)
        unique_together = ("project", "milestone",)
        verbose_name_plural = "Project Milestones"
        
    def __unicode__(self):
        '''Return a string that include the project code and milestone label'''
        return "%s - %s" % (self.project.PRJ_CD, self.milestone.label)

    def __str__(self):
        return self.milestone.label


# TODO Complete the pre_save signal to ProjectMilestones - send
# message to appropriate people whenever

# a record in this table is added or updated.
##  @receiver(pre_save, sender=ProjectMilestones)
##  def send_notices_if_projmilestones_changed(sender, instance, **kwargs):
##      '''If the status of a milestone has changed, send a message to
##      the project lead, their supervisor,
##      the data custodian (and perhaps someday, the operations team).'''
##      try:
##          original = ProjectMilestones.objects.get(pk=instance.pk)
##      except ProjectMilestones.DoesNotExist:
##          #in this case, there was no original - nothing to do
##          pass
##      else:
##          print "%s was Updated. %s is not %s.\n" % (instance.project.PRJ_CD, 
##                                         instance.milestone.label,
##                                         instance.milestone.completed)
##          pass
##  
##      #see if there is a difference between original and the new
##      #instance.  If they are different send an appropriate message to
##      #the appropriate people.
##  

##    Conducted
##    FieldWorkComplete
##    AgeStructures
##    DataScrubbed
##    DataMerged
##    SignOff

        
class Report(models.Model):
    '''class for reports.  A single report can be linked to multiple
    entries in Project Reports'''
    current = models.BooleanField(default=True)
    projectreport = models.ManyToManyField('ProjectMilestones')
    report_path = models.FileField(upload_to="reports/")
    uploaded_on = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length = 300)
    report_hash = models.CharField(max_length = 300)

    def __unicode__(self):
        '''Use the file path as the string representation of a report'''
        return str(self.report_path)


class Bookmark(models.Model):
    '''a class to allow users to bookmark and unbookmark their
    favourite projects.'''
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User, related_name = "project_bookmark")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        '''return the name of the associated project as our representation'''
        return "%s" % self.project

    def get_project_url(self):
        '''Use the url of the project for the bookmark too.'''
        return self.project.get_absolute_url()

    def name(self):
        '''Use the project name for the bookmark too.'''
        return self.project.PRJ_NM
        
    def get_project_code(self):
        '''Use the project code for the bookmark too.'''
        return self.project.PRJ_CD

    def project_type(self):
        '''Use the project type for the bookmark too.'''
        return self.project.project_type

    def prj_ldr(self):
        '''Use the project leader for the bookmark too.'''
        return self.project.prj_ldr

    def year(self):
        '''Use the project year for the bookmark too.'''
        return self.project.year

class Family(models.Model):
    '''Provides a mechanism to ensure that families are unique and
    auto-created.  The relationship between projects and families is
    essentailly an m2m, but currently djagno does not provide a
    mechanism to ensure that each project is associated with just one
    family.'''
    id = models.AutoField(primary_key=True)

    class Meta:
        verbose_name_plural = "Families"

    def __unicode__(self):
        '''A simple string representation'''
        return str("Family %s" % self.id)
        
    
class ProjectSisters(models.Model): 
    '''Sister projects have common presentations and summary reports.
    They must be the same project type, and run in the same year.'''  

    project = models.ForeignKey('Project') 
    family = models.ForeignKey('Family') 

    class Meta:
        verbose_name_plural = "Project Sisters"
        ordering = ['family', 'project']

    def __unicode__(self):
        '''Return the project and family as a string'''
        return str("Project - %s - Family %s" % (self.project, self.family))


class Employee(models.Model):
    '''The employee model is an extension to the user model that captures
    the hierachical employee-supervisor relationship between users.'''
    ROLL_CHOICES = {
        ('manager', 'Manager'),
        ('dba', 'DBA'),    
        ('employee', 'Employee'),
    }

    user = models.ForeignKey(User, unique=True, related_name='employee')
    position = models.CharField(max_length=60)
    role = models.CharField(max_length=30, choices=ROLL_CHOICES,
                                default='Employee')
    lake = models.ManyToManyField('Lake')
    supervisor = models.ForeignKey('self',
                                   blank=True,
                                   null=True)

    def __unicode__(self):
        '''Use the username of the Employee as the string representation'''
        return self.user.username


class Message(models.Model):
    '''A table to hold all of our messages and which project and milestone
    they were associated with.'''
    #(database, display)
    LEVEL_CHOICES = {
        ('info', 'Info'),
        ('actionrequired', 'Action Required'),    
    }

    msg = models.CharField(max_length=100)
    project_milestone = models.ForeignKey(ProjectMilestones)
    #these two fields will allow us to keep track of why messages were sent:

    #we will need a project 'admin' to send announcements
    #"Notification system is now working."
    #"Feature Request/Bug Reporting has been implemented."
    level = models.CharField(max_length=30, choices=LEVEL_CHOICES,
                                default='info')

    def __unicode__(self):
        '''return the messsage as it's unicode method.'''
        return self.msg

    
class Messages2Users(models.Model):
    '''a table to associated messages with users and keep track of when
    they were create and when they were read.'''
    user = models.ForeignKey(User)
    msg = models.ForeignKey(Message)
    created = models.DateTimeField(auto_now_add=True)
    read = models.DateTimeField(blank=True, null=True)


def send_message(msgtxt, users, project, milestone):

    '''Create a record in the message database and send it to each user in
    users by appending a record to Messages2Users for each one.'''

    #if the Project Milestone doesn't exist for this project and
    #milestone create it
    #pdb.set_trace()
    #prjms, created = 
    #                                                    
    ProjectMilestones.objects.get_or_create(project=project, 
                                            milestone=milestone)
    #prjms = ProjectMilestones.objects.get(project=project, milestone=milestone)
    
    #create a message object using the message text and the project-milestone
    message = Message.objects.create(msg=msgtxt, ProjectMilestone=prjms)
    #then loop through the list of users and add one record to 
    #Messages2Users for each one:
    try:
        for emp in users:
            user = User.objects.get(Employee=emp)
            Messages2Users.objects.create(user=user, msg=message)
    except TypeError:
        Messages2Users.objects.create(user=users, msg=message)


def my_messages(user, only_unread=True):
    '''Return a queryset of messages for the user, sorted in reverse
    chronilogical order (newest first).  By default, only unread messages
    are returned, but all messages can be retrieved.'''

    if only_unread:
        my_msgs = (Messages2Users.objects.filter(user=user, 
                            read__isnull=True).order_by('-created'))
    else:
        my_msgs = Messages2Users.objects.filter(user=user).order_by('-created')
    return(my_msgs)

        
class Admin_Milestone(admin.ModelAdmin):
    '''Admin class for milestones'''
    list_display = ('label', 'report', 'category', 'protected',)

class Admin_ProjectType(admin.ModelAdmin):
    '''Admin class for Project Types'''
    pass

class Admin_Database(admin.ModelAdmin):
    '''Admin class for databases'''
    pass

class Admin_Lake(admin.ModelAdmin):
    '''Admin class for lakes'''
    pass

class Admin_Project(admin.ModelAdmin):
    '''Admin class for Projects'''
    pass

class Admin_Family(admin.ModelAdmin):
    '''Admin class for familiy table'''
    pass

class Admin_ProjectSisters(admin.ModelAdmin):
    '''Admin class for project-sisters table'''
    pass

class Admin_ProjectMilestones(admin.ModelAdmin):
    '''Admin class for project - milestones'''
    list_display = ('project', 'milestone',)
    list_filter = ('project', 'milestone')

class Admin_Report(admin.ModelAdmin):
    '''Admin class for reprorts'''
    list_display = ('current', 'report_path', 'uploaded_on', 'uploaded_by')

class Admin_Employee(admin.ModelAdmin):
    '''Admin class for Employees'''
    pass

admin.site.register(Milestone, Admin_Milestone)
admin.site.register(ProjectType, Admin_ProjectType)
admin.site.register(Database, Admin_Database)
admin.site.register(Lake, Admin_Lake)
admin.site.register(Project, Admin_Project)
admin.site.register(ProjectMilestones, Admin_ProjectMilestones)
admin.site.register(Report, Admin_Report)
admin.site.register(Family, Admin_Family)
admin.site.register(ProjectSisters, Admin_ProjectSisters)
admin.site.register(Employee, Admin_Employee)


