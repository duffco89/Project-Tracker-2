from django.contrib import admin

from django.contrib.auth import User

from pjtk2.models import (Milestone, ProjectType, Database, Project,
                          Report, Lake, Family, Employee, ProjectMilestones,
                          ProjectSisters, Message, Messages2Users)


class Admin_Milestone(admin.ModelAdmin):
    '''Admin class for milestones'''
    list_display = ('label', 'order', 'report', 'category', 'protected',)
    ordering = ('order',)

    def queryset(self, request):
         return Milestone.allmilestones


class Admin_ProjectType(admin.ModelAdmin):
    '''Admin class for Project Types'''
    list_display = ('project_type', 'field_component',)


class Admin_Database(admin.ModelAdmin):
    '''Admin class for databases'''
    pass


class Admin_Lake(admin.ModelAdmin):
    '''Admin class for lakes'''
    pass


class Admin_Project(admin.ModelAdmin):
    '''Admin class for Projects'''
    list_display = ('year', 'prj_cd', 'prj_nm','prj_ldr', 'project_type')
    list_filter = ('project_type','year', 'prj_ldr', 'lake')


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
    list_display = ('user', 'position', 'role','get_lakes', 'supervisor')


class Admin_Message(admin.ModelAdmin):
    '''Admin class for Messages'''
    list_display = ('msgtxt', 'prj_cd')

    def prj_cd(self, obj):
        return obj.project_milestone.project.prj_cd


class Admin_Messages2Users(admin.ModelAdmin):
    '''Admin class for Messages2Users'''
    list_display = ('message', 'user', 'prj_cd', 'milestone')
    list_filter = ('user', 'message')

    def prj_cd(self, obj):
        return obj.message.project_milestone.project.prj_cd

    def milestone(self, obj):
        return obj.message.project_milestone.milestone



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
admin.site.register(Message, Admin_Message)
admin.site.register(Messages2Users, Admin_Messages2Users)
