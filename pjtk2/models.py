
# E1101 - Class 'whatever' has no 'something' member
# E1120 - No value passed for parameter 'cls' in function call
#pylint: disable=E1101, E1120

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.contrib.gis.db import models
from taggit.managers import TaggableManager

from markdown2 import markdown

import datetime
import os
import pytz

from pjtk2.functions import get_supervisors, replace_links


LINK_PATTERNS = getattr(settings, "LINK_PATTERNS", None)
#for markdown2 (<h1> becomes <h3>)
DEMOTE_HEADERS = 2


class ProjectsManager(models.GeoManager):
    '''Custom extensions to the base manager for project objects to
    return approved and completed projects.'''

    def get_query_set(self):
        #by default, only return projects that are active:
        return super(ProjectsManager, self).get_query_set().filter(active=True)

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
        approved, but have not been completed or cancelled.
        '''
        return self.filter(active=True, cancelled=False,
                           projectmilestones__milestone__label='Approved',
                           projectmilestones__completed__isnull=False).filter(
                               projectmilestones__milestone__label='Sign off',
                               projectmilestones__completed__isnull=True)


    def cancelled(self):
        '''return a queryset containing only those projects that have been
        cancelled.
        '''
        return self.filter(active=True,cancelled=True)

    def completed(self):
        '''return a queryset containing only those projects that have been
        both approved and completed but not cancelled.
        '''
        return self.filter(active=True, cancelled=False,
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
            year=year, active=True)


class MilestoneManager(models.Manager):
    '''Sumbitted milestone is created automatically when a project is
    created, and is needed for messages, but is not used anywhere else.
    This manager will auto-matically remove it from the returned
    recordsets.
    '''

    def shared(self):
        '''return only those milestones that are shared among sister
        projects'''
        return super(MilestoneManager, self).get_query_set().filter(
                     shared=True)

    def get_query_set(self):
        use_for_related_fields = True
        return super(MilestoneManager, self).get_query_set().exclude(
                     label='Submitted')


class MessageManager(models.Manager):
    '''We only want messages for projects that continue to be active.
    '''
    def get_query_set(self):
        use_for_related_fields = True
        return super(MessageManager, self).get_query_set().filter(
            project_milestone__project__active=True)


class Messages2UsersManager(models.Manager):
    '''We only want messages for projects that continue to be active.
    '''
    def get_query_set(self):
        use_for_related_fields = True
        return super(Messages2UsersManager, self).get_query_set().filter(
            message__project_milestone__project__active=True)


class Milestone(models.Model):
    '''Look-up table of reporting milestone and their attributes.  Not all
    milestones will have a report associated with them.  Keeping
    milestones in a separate tables allows us to dynamically add and
    remove milestones associated with individual projects or project
    types (field projects vs synthesis projects).

    Protected is used to limit who can update various milestones.
    '''

    #(database, display)
    MILESTONE_CHOICES = {
        ('Core', 'core'),
        ('Suggested', 'suggested'),
        ('Custom', 'custom'),
    }

    label = models.CharField(max_length=50, unique=True)
    label_abbrev = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=30, choices=MILESTONE_CHOICES,
                                default='Custom')
    report = models.BooleanField(default=False)
    #should this milestone be shared among sister projects?
    shared = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)
    order = models.FloatField(default=99)

    objects = MilestoneManager()
    allmilestones = models.Manager()

    class Meta:
        verbose_name = "Milestone List"
        verbose_name_plural = "Milestones List"
        ordering = ['-report', 'order']

    def __unicode__(self):
        return self.label




class ProjectType(models.Model):
    '''A look-up table to hold project types'''
    project_type = models.CharField(max_length=150)
    field_component  = models.BooleanField(default=True)

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

    active  = models.BooleanField(default=True)
    cancelled  = models.BooleanField(default=False)
    cancelled_by  = models.ForeignKey(User, related_name="Cancelled By",
                                  blank=True, null=True)
    year = models.CharField("Year", max_length=4, blank=True, editable=False)
    prj_date0 = models.DateField("Start Date", blank=False)
    prj_date1 = models.DateField("End Date", blank=False)
    prj_cd = models.CharField("Project Code", max_length=12, unique=True,
                              blank=False)
    prj_nm = models.CharField("Project Name", max_length=60, blank=False)
    prj_ldr = models.ForeignKey(User, related_name="Project Lead")
    field_ldr = models.ForeignKey(User, related_name="Field Lead",
                                  blank=True, null=True)
    comment = models.TextField(blank=False,
                               help_text="General project description.")
    comment_html = models.TextField(blank=True, null=True,
                               help_text="General project description.")
    help_str = "Potential risks associated with not running project."
    risk = models.TextField("Risk", null=True, blank=True,
                            help_text=help_str)
    risk_html = models.TextField("Risk", null=True, blank=True,
                            help_text=help_str)
    master_database = models.ForeignKey("Database", null=True, blank=True)
    project_type = models.ForeignKey("ProjectType", null=True, blank=True)
    owner = models.ForeignKey(User, blank=True, related_name="ProjectOwner")
    dba = models.ForeignKey(User, blank=True, related_name="ProjectDBA")
    funding = models.CharField("Funding Source", max_length=30,
                               choices=FUNDING_CHOICES, default="spa")
    lake = models.ForeignKey(Lake, default=1)
    odoe = models.DecimalField("ODOE", max_digits=8, default=0,
                                     decimal_places=2, null=True, blank=True)
    salary = models.DecimalField("Salary", max_digits=8, default=0,
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
            #ProjectMilestones.objects.filter(project=self,
            #                         milestone__label='Approved').update(
            #                             completed=now)
            prjms = ProjectMilestones.objects.get(project=self,
                                                  milestone__label='Approved')
            prjms.completed = now
            #save sends pre_save signal
            prjms.save()
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
            #ProjectMilestones.objects.filter(project=self,
            #                     milestone__label='Approved').update(
            #                         completed=None)
            prjms = ProjectMilestones.objects.get(project=self,
                                                  milestone__label='Approved')
            prjms.completed = None
            #save sends pre_save signal
            prjms.save()

        except ProjectMilestones.DoesNotExist:
            pass


    def is_approved(self):
        '''Is the current project approved?  Returns true if it is, otherwize
        false.'''
        approved = ProjectMilestones.objects.get(project=self,
                                                 milestone__label='Approved')
        if approved.completed is not None:
            return(True)
        else:
            return(False)

    def signoff(self):
        '''A helper function to make it easier to sign off a project'''
        #TODO - add logic here to make sure all previous requirements
        #have been met! - can't signoff on a project that wasn't
        #approved or compelted.
        now = datetime.datetime.now(pytz.utc)
        milestone= Milestone.objects.get(label__iexact='Sign Off')
        prjms, created= ProjectMilestones.objects.get_or_create(
                project=self, milestone=milestone)

        prjms.completed = now
        prjms.save()


    def is_complete(self):
        '''Is the current project completed (ie. signoff=True)?  Returns true
        if it is, otherwise false.
        '''
        completed = ProjectMilestones.objects.get(project=self,
                                                  milestone__label__iexact='Sign Off')
        if completed.completed is not None:
            return(True)
        else:
            return(False)


    def status(self):
        """The status of a project must be one of: 'Submitted', 'Ongoing',
        'Cancelled' or 'Complete'
        Submitted - not approved
        Ongoing - approved, but not cancelled or signed off
        Cancelled - cancelled==True
        Complete - signoff==True

        NOTE - projects cannot be completed or caneled withouth being
        approved first!  Similarly, cancelled projects cannot be complete.

        """

        if not self.is_approved():
            return('Submitted')
        elif self.cancelled:
            return('Cancelled')
        elif self.is_complete():
            return('Complete')
        else:
            return('Ongoing')




    def project_suffix(self):
        '''return the prject suffix for the given project'''
        return self.prj_cd[-3:]

    def name(self):
        '''alias for prj_nm - maintains fishnetII name in model but works
         with django convention of obj.name.'''
        return self.prj_nm

    def description(self):
        '''alias for comment - maintains fishnetII comment in model but works
         with django convention of obj.description.'''
        return self.comment

    def __unicode__(self):
        '''Return the name of the project and it's project code'''
        ret = "%s (%s)" % (self.prj_nm, self.prj_cd)
        return ret

    def get_milestones(self, required=True):
        '''get all of the milestone events that have been assigned to
        this project - (these are just milestone events where report==False)'''
        if required is True:
            return ProjectMilestones.objects.filter(project=self,
                                                    required=True,
                                                    milestone__report=False
                                                  ).order_by('milestone__order')
        else:
            return ProjectMilestones.objects.filter(project=self,
                                                    milestone__report=False
                                                  ).order_by('milestone__order')

    def get_reporting_requirements(self):
        '''get all of the reports have been assigned to
        this project - no distinction between core or custom reports'''
        return ProjectMilestones.objects.filter(project=self,
                                                milestone__report=True
                                                ).order_by('milestone__order')

    def get_uploaded_reports(self):
        '''get all of the CURRENT reports that are associated with this
        project.  Non-current reports are not included in this
        recordset.
        '''
        #TODO Filter for report=True
        return Report.objects.filter(current=True,
                                     projectreport__project=self)


    def get_associated_files(self):
        '''get all of the associated files associated with this project
        Associated files are not associated with a milesone and are
        likely to be different for each project..

        '''

        return AssociatedFile.objects.filter(project=self)



    def get_core_assignments(self, all_reports=True):
        '''get all of the core reports have been assigned to this project, if
        'all_reports' is true, all assignements are returned, if 'all_reports'
        is False, only required assignments are returned.

        '''

        if all_reports is True:
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
        customreports = Milestone.objects.filter(category='Custom',
                                                 report=True)

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


    def milestone_complete(self, milestone):
        """This is a helper function used in to manage project reporting
        requirements. It returns True if the milestone has been
        completed for a project, it returns False if a require element
        has not been completed, and returns None if the milestone does
        not exist or was not requested for this project.

        Arguments:
        - `self`: a project object
        - `milestone`: a milestone object

        """

        try:
            pms = ProjectMilestones.objects.get(project=self,
                                                milestone=milestone)
            if pms.completed:
                # - requested, done = True
                # - not requested, done anyway = True
                return True
            elif pms.required:
                #-requested, not done = False
                return False
            else:
                #-not requested, not done - None
                return None
        except (ProjectMilestones.DoesNotExist, ValueError) as e:
            return None


    def initialize_milestones(self):
        '''A function that will add a record into "ProjectMilestones" for
        each of the core reports and milestones for newly created projects'''

        corereports = Milestone.allmilestones.filter(category='Core')
        for report in corereports:
            if report.label == 'Submitted':
                now = datetime.datetime.now(pytz.utc)
            else:
                now = None
            ProjectMilestones.objects.get_or_create(project=self,
                                                    milestone = report,
                                                    completed = now)

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

    def has_sister(self):
        '''a simple little helper function - returns True if this project has
        one or more sisters, False otherwise.  Used in templates to
        issue warnings about cascading effects on other projects.
        '''
        if len(self.get_sisters()):
            return(True)
        else:
            return(False)

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
                        slug=self.slug).order_by('slug')
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
            self.slug = slugify(self.prj_cd)
            self.year = self.prj_date0.year
            new = True

        if self.comment:
            self.comment_html = markdown(self.comment, extras={'demote-headers':
                                                               DEMOTE_HEADERS,})
            self.comment_html = replace_links(self.comment_html,
                                              link_patterns=LINK_PATTERNS)
        if self.risk:
            self.risk_html = markdown(self.risk,extras={'demote-headers':
                                                        DEMOTE_HEADERS,})
            self.risk_html = replace_links(self.risk_html,
                                              link_patterns=LINK_PATTERNS)

        super(Project, self).save( *args, **kwargs)
        if new:
            self.initialize_milestones()


    def get_sample_points(self):
        '''get the coordinates of sample points associated with this
        project.  Returns a list of tuples.  Each tuple contains the
        sample id, dd_lat and dd_lon

        '''
        points = SamplePoint.objects.filter(project__id=self.id).values_list(
            'sam', 'geom')

        return points


    def total_cost(self):
        '''a little helper function to calculate the total cost of a project
        (sum of salary and odoe)'''
        salary = self.salary if self.salary is not None else 0
        odoe = self.odoe if self.odoe is not None else 0
        return salary + odoe


class SamplePoint(models.Model):
    '''A class to hold the sampling locations of a project.  In most
    cases, a samplePoint instance represents a net in the water, but
    can have different meaning for different projects.
    '''
    project = models.ForeignKey('Project')
    sam  = models.CharField(max_length=30, null=True, blank=True)
    geom = models.PointField(srid=4326,
                             help_text='Represented as (longitude, latitude)')

    objects = models.GeoManager()


#class ProjectPoly(models.Model):
#    '''A class to hold the convex hull derived from the sampling locations
#    of a project.  Calculated when sample points are uploaded into
#    project tracker.  Makes spatial queries much faster - query few
#    polygons instead of lots and lots of individual points.
#
#    '''
#    project = models.ForeignKey('Project')
#    geom = models.PolygonField(srid=4326)
#    objects = models.GeoManager()


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
        return "%s - %s" % (self.project.prj_cd, self.milestone.label)

    def __str__(self):
        return self.milestone.label


class Report(models.Model):
    '''class for reports.  A single report can be linked to multiple
    entries in Project Reports'''
    current = models.BooleanField(default=True)
    projectreport = models.ManyToManyField('ProjectMilestones')
    report_path = models.FileField(upload_to="milestone_reports/",
                                   max_length=200)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    #uploaded_by = models.CharField(max_length = 300)
    uploaded_by = models.ForeignKey(User)
    report_hash = models.CharField(max_length = 300)

    def __unicode__(self):
        '''Use the file path as the string representation of a report'''
        return str(self.report_path)


class AssociatedFile(models.Model):
    '''class for associated files.  Unlike reports, an associated file can
    only be linked to a single project
    '''

    def get_associated_file_upload_path(self, filename):
        '''a little helper function used by "upload_to" of associated files.
        It will save all of the files associated with a project in a project
        specific directory (named using the project code)
        '''
        val = os.path.join('associated_files',
                           self.project.prj_cd, filename)
        return val


    project = models.ForeignKey(Project)
    file_path = models.FileField(upload_to=get_associated_file_upload_path,
                                 max_length=200)
    current = models.BooleanField(default=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User)
    hash = models.CharField(max_length=300)

    def __unicode__(self):
        '''Use the file path as the string representation of a report'''
        return str(self.file_path)

    #def get_project_code(self):
    #    '''return the project code of the project this file is associated
    #    with.  Used to build upload_to path'''
    #    pass


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

    def get_watchers(self):
        '''Return the list of user who are currently watching a particular
        project'''
        bookmarks = Bookmark.objects.filter(project=self.project)
        watchers = [x.user for x in bookmarks]
        return watchers

    def get_project_url(self):
        '''Use the url of the project for the bookmark too.'''
        return self.project.get_absolute_url()

    def name(self):
        '''Use the project name for the bookmark too.'''
        return self.project.prj_nm

    def get_project_code(self):
        '''Use the project code for the bookmark too.'''
        return self.project.prj_cd

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
    #supervisor = models.ForeignKey(User, unique=False, blank=True, null=True,
    #                               related_name='supervisor')

    def __unicode__(self):
        '''Use the username of the Employee as the string representation'''
        return self.user.username

    def get_lakes(self):
        return ", ".join([l.lake for l in self.lake.all()])


class Message(models.Model):
    '''A table to hold all of our messages and which project and milestone
    they were associated with.'''
    #(database, display)
    distribution_list = models.ManyToManyField(User, through='Messages2Users')

    msgtxt = models.CharField(max_length=100)
    project_milestone = models.ForeignKey(ProjectMilestones)
    #these two fields will allow us to keep track of why messages were sent:

    #we will need a project 'admin' to send announcements
    #"Notification system is now working."
    #"Feature Request/Bug Reporting has been implemented."

    LEVEL_CHOICES = {
        ('info', 'Info'),
        ('actionrequired', 'Action Required'),
    }

    level = models.CharField(max_length=30, choices=LEVEL_CHOICES,
                             default='info')

    objects = MessageManager()

    def __unicode__(self):
        '''return the messsage as it's unicode method.'''
        return self.msgtxt


class Messages2Users(models.Model):
    '''a table to associated messages with users and keep track of when
    they were create and when they were read.'''

    user = models.ForeignKey(User)
    message = models.ForeignKey(Message)
    created = models.DateTimeField(auto_now_add=True)
    read = models.DateTimeField(blank=True, null=True)

    objects = Messages2UsersManager()

    class Meta:
        unique_together = ("user", "message",)
        verbose_name_plural = "Messages2Users"

    def __unicode__(self):
        '''return the messsage as it's unicode method.'''
        return "%s - %s" % (self.user, self.message)

    def mark_as_read(self):
        self.read = datetime.datetime.now(pytz.utc)
        self.save()



#=========================
#   Message functions

def build_msg_recipients(project, level=None, dba=True, ops=True):
    '''A function to complile the list of recipients for messages

    project - a project instance
    level - an integer indicating how high up the employee hierarchy the
             message should propegate (not yet implemented)
    dba - should the project's dba be notified too?
    ops - should the designated operations coordinator(s) be nofitied
             (also not yet implemented)
    The function returns a list of unique user instances.
    '''

    prj_owner = project.owner
    prj_owner = Employee.objects.get(user__username=prj_owner)
    recipients = get_supervisors(prj_owner)
    #convert the employees to user objects
    recipients = [x.user for x in recipients]

    if level and level < len(recipients):
        #trim the list of supervisors here (if appropriate)
        recipients = recipients[:-(level-1)]
    #Find out who is watching this project and add them to the list too
    bookmarks = Bookmark.objects.filter(project=project)
    if bookmarks.exists():
        for watcher in bookmarks:
            recipients.append(watcher.user)
    #send notice to dba too
    if dba:
        recipients.append(project.dba)
    if ops:
        #recipients.append(project.ops)
        pass
    #remove any duplicates
    recipients = list(set(recipients))
    return(recipients)


def send_message(msgtxt, recipients, project, milestone):
    '''Create a record in the message database and send it to each user in
    recipients by appending a record to Messages2Users for each one.'''

    #if the Project Milestone doesn't exist for this project and
    #milestone create it
    prjms, created = ProjectMilestones.objects.get_or_create(project=project,
                                            milestone=milestone)

    #create a message object using the message text and the project-milestone
    message = Message.objects.create(msgtxt=msgtxt, project_milestone=prjms)
    #then loop through the list of recipients and add one record to
    #Messages2Users for each one:
    try:
        for recipient in recipients:
            #user = User.objects.get(Employee=emp)
            #Messages2Users.objects.create(user=recipient, msg=message)
            msg4u = Messages2Users(user=recipient, message=message)
            msg4u.save()
    except TypeError:
        #Messages2Users.objects.create(user=recipients, msg=message)
        msg4u = Messages2Users(user=recipients, message=message)
        msg4u.save()


#=====================================
#    Signals

# TODO Complete the pre_save signal to ProjectMilestones - send
# message to appropriate people whenever a record in this table is
# added or updated.

@receiver(pre_save, sender=ProjectMilestones)
def send_notice_prjms_changed(sender, instance, **kwargs):
    '''If the status of a milestone has changed, send a message to the
    project lead, their supervisor, the data custodian (and perhaps
    someday, the operations team).  Note that 'submitted' milestone
    need to be handled using a post_save signal.
    '''

    msgtxt = ""

    try:
        original = ProjectMilestones.objects.get(pk=instance.pk)
    except ProjectMilestones.DoesNotExist:
        #in this case, there was no original.
        original = None

    #if we found an original projectmilestone,
    if original:
        #find out if 'completed' has changed and whether or not it is now
        #empty and build an appropriate message
        if instance.completed != original.completed and instance.completed:
            #this milestone has been satisfied
            msgtxt = instance.milestone.label

        elif instance.completed != original.completed and original.completed:
            #this milestone has been 'un-approved'
            msgtxt = ("The milestone '%s' has been revoked"
                    %  instance.milestone.label)
    if msgtxt:
        #build the list of people we will be sending the message to
        recipients = build_msg_recipients(instance.project)
        send_message(msgtxt, recipients, project=instance.project,
                    milestone=instance.milestone)

#pre_save.connect(send_notice_prjms_changed, sender=ProjectMilestones)

@receiver(post_save, sender=ProjectMilestones)
def send_notice_project_submitted(sender, instance, **kwargs):
    '''If the status of a milestone has changed, send a message to the
    project lead, their supervisor, the data custodian (and perhaps
    someday, the operations team).  Note that 'submitted' milestone
    need to be handled using a post_save signal.
    '''

    if instance.milestone.label == 'Submitted':
        msgtxt = 'Submitted'
        recipients = build_msg_recipients(instance.project)
        send_message(msgtxt, recipients, project=instance.project,
                    milestone=instance.milestone)
