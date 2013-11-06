from django.contrib import admin

from pjtk2.models import (Milestone, ProjectType, Database, Project,
                          Report, Lake, Family, Employee, ProjectMilestones,
                          ProjectSisters)


class Admin_Milestone(admin.ModelAdmin):
    '''Admin class for milestones'''
    list_display = ('label', 'order', 'report', 'category', 'protected',)

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

