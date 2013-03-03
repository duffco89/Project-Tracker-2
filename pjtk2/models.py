from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse


# Create your models here.

MILESTONE_CHOICES = {
    ('Core','core'),
    ('Suggested','suggested'),    
    ('Custom','custom'),
}

class Milestone(models.Model):
    '''Look-up table of reporting milestone'''
    label = models.CharField(max_length=30)
    category = models.CharField(max_length=30, choices=MILESTONE_CHOICES)
    order = models.IntegerField()

    class Meta:
        verbose_name = "Reporting Milestones"
        verbose_name_plural = "Reporting Milestones"
        ordering = ['order']


    def __unicode__(self):
        return self.label


class TL_ProjType(models.Model):
    Project_Type = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Project Type"
    
    def __unicode__(self):
        return self.Project_Type

class TL_Database(models.Model):
    MasterDatabase = models.CharField(max_length=250)
    Path = models.CharField(max_length=250)

    class Meta:
        verbose_name = "Master Database"
    
    def __unicode__(self):
        return self.MasterDatabase

class Project(models.Model):
    '''Class to hold a record for each project'''
    YEAR = models.CharField(max_length=4, blank=True, editable=False)
    PRJ_DATE0 = models.DateField("Start Date", blank=False)
    PRJ_DATE1 = models.DateField("End Date", blank=False)
    PRJ_CD = models.CharField("Project Code", max_length=12, unique=True, blank=False)
    PRJ_NM = models.CharField("Proejct Name", max_length=50, blank=False)
    PRJ_LDR = models.CharField("Project Lead", max_length=40, blank=False)
    COMMENT = models.TextField(blank=False)
    MasterDatabase = models.ForeignKey("TL_Database")
    ProjectType = models.ForeignKey("TL_ProjType")

    Approved = models.BooleanField(default = False)
    Conducted  = models.BooleanField(default = False)
    FieldWorkComplete  = models.BooleanField(default = False)
    AgeStructures = models.BooleanField(default = False)
    DataScrubbed  = models.BooleanField(default = False)
    DataMerged  = models.BooleanField(default = False)
    SignOff  = models.BooleanField(default = False)
    
    Max_DD_LAT = models.DecimalField(max_digits=5, decimal_places=3, 
                                     null=True, blank=True)
    Min_DD_LAT = models.DecimalField(max_digits=5, decimal_places=3, 
                                     null=True, blank=True)
    Max_DD_LON = models.DecimalField(max_digits=5, decimal_places=3, 
                                     null=True, blank=True)
    Min_DD_LON = models.DecimalField(max_digits=5, decimal_places=3, 
                                     null=True, blank=True)
    Owner = models.ForeignKey(User, blank=True)
    #Owner = models.CharField(max_length=40,blank=True)
    slug = models.SlugField(blank=True, editable=False)

    class Meta:
        verbose_name = "Project List"
        ordering = ['-PRJ_DATE1']

    def ProjectSuffix(self):
        return self.PRJ_CD[-3:]

    def __unicode__(self):
        ret = "%s (%s)" % (self.PRJ_NM, self.PRJ_CD)
        return ret

    def get_reports(self):
        '''get all of the reports that are currenly associated with
        this project'''
        return Report.objects.filter(projectreport__project=self)

    def get_assignments(self):
        '''get all of the reports have been assigned to 
        this project'''
        return ProjectReports.objects.filter(project=self)


    def get_completed(self):
        '''get the project reports that have uploaded reports
        associated with them.'''
        return ProjectReports.objects.filter(project=self).filter(report__in=Report.objects.filter(projectreport__project=self))


    def get_outstanding(self):
        return ProjectReports.objects.filter(project=self).exclude(report__in=Report.objects.filter(projectreport__project=self))


    def resetMilestones(self):
        '''a function to make sure that all of the project milestones are
        set to zero. Used when copying an existing project - we don't want
        to copy its milestones too'''
        self.Approved = False
        self.Conducted = False
        self.DataScrubbed = False
        self.DataMerged = False                        
        self.SignOff = False
        return self



    #@models.permalink
    def get_absolute_url(self):
        #slug = str(self.slug)
        url = reverse('pjtk2.views.ProjectDetail', kwargs={'slug':self.slug})
        return url

    def save(self, *args, **kwargs):
        """
        from:http://stackoverflow.com/questions/7971689/
             generate-slug-field-in-existing-table
        Slugify name if it doesn't exist. IMPORTANT: doesn't check to see
        if slug is a dupicate!
        """
        if not self.slug:
            self.slug = slugify(self.PRJ_CD)
        if not self.YEAR:            
            self.YEAR = self.PRJ_DATE0.year
        super(Project, self).save( *args, **kwargs)

    

class ProjectReports(models.Model):
    '''list of reporting requirements for each project'''
    project = models.ForeignKey('Project')
    report_type = models.ForeignKey('Milestone')

    class Meta:
        unique_together = ("project", "report_type",)
        verbose_name_plural = "Project Reports"
        
    def __unicode__(self):
        return "%s - %s" % (self.project.PRJ_CD, self.report_type)

        
        
class Report(models.Model):
    '''class for reports.  A single report can be linked to multiple
    entries in Project Reports'''
    current = models.BooleanField(default=True)
    #projectreport = models.ManyToManyField('ProjectReports')
    projectreport = models.ForeignKey('ProjectReports')
    #report_path = models.CharField(max_length = 300, default="")
    report_path = models.FileField(upload_to="reports/")
    uploaded_on = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length = 300)
    report_hash = models.CharField(max_length = 300)

    def __unicode__(self):
        return str(self.report_path)

        
class AdminMilestone(admin.ModelAdmin):
    list_display = ('label', 'category',)


class AdminTL_ProjType(admin.ModelAdmin):
    pass

class AdminTL_Database(admin.ModelAdmin):
    pass

class AdminProject(admin.ModelAdmin):
    pass

class AdminProjectReports(admin.ModelAdmin):
    list_display = ('project', 'report_type',)
    list_filter = ('project', 'report_type')

class AdminReport(admin.ModelAdmin):
    #list_display = ('current', 'ProjectReports_project', 'ProjectReports_report__type',)
    list_display = ('current', 'report_path','uploaded_on', 'uploaded_by')
    #    list_filter = ('ProjectReports__project',)



admin.site.register(Milestone, AdminMilestone)
admin.site.register(TL_ProjType, AdminTL_ProjType)
admin.site.register(TL_Database, AdminTL_Database)
admin.site.register(Project, AdminProject)
admin.site.register(ProjectReports, AdminProjectReports)
admin.site.register(Report, AdminReport)
