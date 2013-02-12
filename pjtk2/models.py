\from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.template.defaultfilters import slugify

# Create your models here.

MILESTONE_CHOICES = {
    ('Common','common'),
    ('Custom','custom'),
}

class Milestone(models.Model):
    '''Look-up table of reporting milestone'''
    label = models.CharField(max_length=30)
    category = models.CharField(max_length=30, choices=MILESTONE_CHOICES)
    order = models.IntegerField()

    class Meta:
        verbose_name = "Reporting Milestones"
        ordering = ['order']


    def __unicode__(self):
        return self.label


class TL_ProjType(models.Model):
    Project_Type = models.CharField(max_length=150)

    def __unicode__(self):
        return self.Project_Type

class TL_DataLocations(models.Model):
    MasterDatabase = models.CharField(max_length=250)
    Path = models.CharField(max_length=250)

    def __unicode__(self):
        return self.MasterDatabase

class Project(models.Model):
    '''Class to hold a record for each project'''
    YEAR = models.CharField(max_length=4)
    PRJ_DATE0 = models.DateField("Start Date", blank=False)
    PRJ_DATE1 = models.DateField("End Date", blank=False)
    PRJ_CD = models.CharField("Project Code", max_length=13, unique=True, blank=False)
    PRJ_NM = models.CharField("Proejct Name", max_length=50, blank=False)
    PRJ_LDR = models.CharField("Project Lead", max_length=40, blank=False)
    COMMENT = models.TextField(blank=False)
    MasterDatabase = models.ForeignKey("TL_DataLocations")
    ProjectType = models.ForeignKey("TL_ProjType")
    Approved = models.BooleanField(default = False)
    SignOff  = models.BooleanField(default = False)
    FieldWorkComplete  = models.BooleanField(default = False)
    AgeStructures = models.BooleanField(default = False)
    DataScrubbed  = models.BooleanField(default = False)
    DataMerged  = models.BooleanField(default = False)
    Conducted  = models.BooleanField(default = False)
    Max_DD_LAT = models.DecimalField(max_digits=5, decimal_places=3)
    Min_DD_LAT = models.DecimalField(max_digits=5, decimal_places=3)
    Max_DD_LON = models.DecimalField(max_digits=5, decimal_places=3)
    Min_DD_LON = models.DecimalField(max_digits=5, decimal_places=3)
    Owner = models.CharField(max_length=40)
    slug = models.SlugField()

    class Meta:
        verbose_name = "Project List"
        ordering = ['-PRJ_DATE1']

    def ProjectSuffix(self):
        return self.PRJ_CD[-3:]

    def __unicode__(self):
        ret = "%s (%s)" % (self.PRJ_NM, self.PRJ_CD)
        return ret

    @models.permalink    
    def get_absolute_url(self):
        ret = "/projects/%s/" % self.slug
        return ret

    def save(self, *args, **kwargs):
        """
        from:http://stackoverflow.com/questions/7971689/
             generate-slug-field-in-existing-table
        Slugify name if it doesn't exist. IMPORTANT: doesn't check to see
        if slug is a dupicate!
        """
        if not self.slug:
            self.slug = slugify(self.PRJ_CD)
        super(Project, self).save( *args, **kwargs)

class ProjectReports(models.Model):
    '''list of reporting requirements for each project'''
    project = models.ForeignKey('Project')
    report_type = models.ForeignKey('Milestone')

    class Meta:
        unique_together = ("project", "report_type",)

    def __unicode__(self):
        return "%s - %s" % (self.project, self.report_type)

class Reports(models.Model):
    '''class for reporting milestones'''
    current = models.BooleanField(default=True)
    #projectreport = models.ManyToManyField('ProjectReports')
    projectreport = models.ForeignKey('ProjectReports')
    report_path = models.CharField(max_length = 300, default="")
    uploaded_on = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length = 300)
    report_hash = models.CharField(max_length = 300)

    def __unicode__(self):
        return self.report_path

class AdminMilestone(admin.ModelAdmin):
    list_display = ('label', 'category',)


class AdminTL_ProjType(admin.ModelAdmin):
    pass

class AdminTL_DataLocations(admin.ModelAdmin):
    pass

class AdminProject(admin.ModelAdmin):
    pass

class AdminProjectReports(admin.ModelAdmin):
    list_display = ('project', 'report_type',)
    list_filter = ('project', 'report_type')

class AdminReports(admin.ModelAdmin):
    #list_display = ('current', 'ProjectReports_project', 'ProjectReports_report__type',)
    list_display = ('current', 'report_path','uploaded_on', 'uploaded_by')
    #    list_filter = ('ProjectReports__project',)



admin.site.register(Milestone, AdminMilestone)
admin.site.register(TL_ProjType, AdminTL_ProjType)
admin.site.register(TL_DataLocations, AdminTL_DataLocations)
admin.site.register(Project, AdminProject)
admin.site.register(ProjectReports, AdminProjectReports)
admin.site.register(Reports, AdminReports)
