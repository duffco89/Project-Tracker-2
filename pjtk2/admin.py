from leaflet.admin import LeafletGeoAdmin
from django import forms
from django.forms import ModelChoiceField
from django.contrib import admin
from django.contrib.auth import get_user_model

from pjtk2.models import (
    Milestone,
    Database,
    FundingSource,
    ProjectType,
    ProjectProtocol,
    Project,
    ProjectFunding,
    Report,
    Family,
    Employee,
    ProjectMilestones,
    ProjectSisters,
    Message,
    Messages2Users,
)

User = get_user_model()


class Admin_Milestone(admin.ModelAdmin):
    """Admin class for milestones"""

    list_display = ("label", "order", "report", "category", "protected")
    ordering = ("order",)

    def queryset(self, request):
        return Milestone.allmilestones


class ProtocolInline(admin.TabularInline):
    """Admin class for Project Protocols"""

    model = ProjectProtocol


class Admin_ProjectProtocol(admin.ModelAdmin):
    """Admin class for Project Protocols"""

    search_fields = ["abbrev", "protocol"]
    list_filter = ("project_type",)
    list_display = ("abbrev", "protocol", "project_type")


class Admin_ProjectType(admin.ModelAdmin):
    """Admin class for Project Types"""

    list_display = ("project_type", "field_component")

    inlines = [ProtocolInline]


class Admin_Database(admin.ModelAdmin):
    """Admin class for databases"""

    pass


class Admin_Project(admin.ModelAdmin):
    """Admin class for Projects"""

    search_fields = ["prj_cd", "prj_nm"]
    list_display = ("prj_cd", "prj_nm", "prj_ldr", "project_type", "year")
    list_filter = ("lake__lake_name", "project_type", "year", "prj_ldr")
    # list_filter = ("project_type", "year", "prj_ldr")


class Admin_FundingSource(admin.ModelAdmin):
    """Admin class for our funding sources"""

    pass


class Admin_ProjectFunding(admin.ModelAdmin):
    """Admin class for our funding sources for each project"""

    pass


class Admin_Family(admin.ModelAdmin):
    """Admin class for familiy table"""

    pass


class Admin_ProjectSisters(admin.ModelAdmin):
    """Admin class for project-sisters table"""

    pass


class Admin_ProjectMilestones(admin.ModelAdmin):
    """Admin class for project - milestones"""

    list_display = ("project", "milestone")
    list_filter = ("project", "milestone")


class Admin_Report(admin.ModelAdmin):
    """Admin class for reprorts"""

    list_display = ("current", "report_path", "uploaded_on", "uploaded_by")


class NameChoiceField(ModelChoiceField):
    """A custom name model form field that displays the users as last
    name, first name.  Used in Employee admin form."""

    def label_from_instance(self, obj):
        if hasattr(obj, "last_name"):
            return f"{obj.last_name}, {obj.first_name}"
        else:
            return f"{obj.user.last_name}, {obj.user.first_name}"


class EmployeeAdminForm(forms.ModelForm):
    """Custome form model that will allow us to add queryset to the choice
    fields taht will limit them to active users and present them in a
    user-friendly manner."""

    # user, position, fol lake, supervisor

    user = NameChoiceField(
        queryset=User.objects.filter(is_active=True).order_by("username")
    )

    supervisor = NameChoiceField(
        queryset=Employee.objects.filter(user__is_active=True).order_by(
            "user__username"
        )
    )

    class Meta:
        model = Employee
        fields = ["user", "position", "role", "lake", "supervisor"]
        field_order = ["user", "position", "role", "lake", "supervisor"]


class Admin_Employee(admin.ModelAdmin):
    """Admin class for Employees"""

    form = EmployeeAdminForm

    def username(self, instance):
        return "{}, {} ({})".format(
            instance.user.last_name, instance.user.first_name, instance.user.username
        )

    search_fields = ["user__first_name", "user__last_name"]
    list_display = ("username", "position", "role", "supervisor")

    def change_view(self, request, object_id, form_url="", extra_context=None):

        obj = self.get_object(request, object_id)
        if extra_context is None:
            extra_context = {}
        extra_context["title"] = "Update employee Attributes for {} {} ({})".format(
            obj.user.first_name, obj.user.last_name, obj.user.username
        )
        return super(Admin_Employee, self).change_view(
            request, object_id, form_url, extra_context
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(user__is_active=True)
            .select_related("user", "supervisor__user")
            .order_by("user__username")
        )


class Admin_Message(admin.ModelAdmin):
    """Admin class for Messages"""

    list_display = ("msgtxt", "prj_cd")

    def prj_cd(self, obj):
        return obj.project_milestone.project.prj_cd


class Admin_Messages2Users(admin.ModelAdmin):
    """Admin class for Messages2Users"""

    list_display = ("message", "user", "prj_cd", "milestone")
    list_filter = ("user", "message")

    def prj_cd(self, obj):
        return obj.message.project_milestone.project.prj_cd

    def milestone(self, obj):
        return obj.message.project_milestone.milestone


admin.site.register(Milestone, Admin_Milestone)
admin.site.register(ProjectType, Admin_ProjectType)
admin.site.register(ProjectProtocol, Admin_ProjectProtocol)
admin.site.register(Database, Admin_Database)
admin.site.register(Project, Admin_Project)
admin.site.register(ProjectMilestones, Admin_ProjectMilestones)
admin.site.register(Report, Admin_Report)
admin.site.register(Family, Admin_Family)
admin.site.register(ProjectSisters, Admin_ProjectSisters)
admin.site.register(Employee, Admin_Employee)
admin.site.register(Message, Admin_Message)
admin.site.register(Messages2Users, Admin_Messages2Users)

admin.site.register(FundingSource, Admin_FundingSource)
admin.site.register(ProjectFunding, Admin_ProjectFunding)
