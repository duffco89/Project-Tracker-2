"""
This file contains a number of helper functions.  Most of the
functions are used in views.py,but they are not views themselves.

"""


import re
import datetime
import pytz

from django.db.models import Subquery, Case, When, BooleanField, F, Value
from django.db.models.functions import Concat

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404


def make_possessive(string):
    """
    A supper simple helper function that will used to make people's
    names possessive.

    If the last letter of the name is an 's', simply append an
    appostrophy, if it is anything else append 's.

    Arguments:
    - `string`:

    """

    if string[-1] == "s":
        string = string + "'"
    else:
        string = string + "'s"
    return string


def strip_carriage_returns(my_string):
    """
    A little helper function to remove carriage returns from text.
    This function is intended to help with artifacts introduced by cutting
    and pasting from word - if people do that, carriage returns are added
    to end of each line.  This fucntion removes those carriage returns
    without disrupting the paragraph structure or markdown.

    Arguments:

    - `my_string`: the string from which to remove extranious
    carriage returns.

    """

    if my_string is None:
        return None

    my_lines = my_string.splitlines()
    for i, x in enumerate(my_lines):
        if x == "" or re.match(r"\s", x):
            my_lines[i] = "\r\n\r\n"
        else:
            my_lines[i] += " "
    return "".join(my_lines).strip()


def get_supervisors(employee):
    """
    Given an employee object, return a list of supervisors.  the first
    element of list will be the intial employee.
    """

    if employee.supervisor:
        return [employee] + get_supervisors(employee.supervisor)
    else:
        return [employee]


def get_minions(employee):
    """
    Given an employee objects, return a list of employees under his/her
    supervision.  The first element of list will be the intial
    employee.
    """

    ret = [employee]
    for minion in employee.employee_set.all():
        # ret.append(get_minions(minion))
        ret.extend(get_minions(minion))
    return ret


def my_messages(user, all=False):
    """
Return a queryset of messages for the user, sorted in reverse
    chronological order (newest first).  By default, only unread messages
    are returned, but all messages can be retrieved."""

    from pjtk2.models import Messages2Users

    my_msgs = (
        Messages2Users.objects.filter(user=user)
        .select_related(
            "user", "message__project_milestone", "message__project_milestone__project"
        )
        .order_by("-created")
    )
    if not all:
        my_msgs = my_msgs.filter(read__isnull=True)

    return my_msgs


def get_messages_dict(messages):
    """
given  notification message, pull out the project, url, id and
    message.  wrap them up in a dict and return it.  The dict is then
    passed to the notifcation form so that each message can be displayed
    and marked as read by the user.

    messages is a list of Messages2Users objects
"""

    initial = []

    for msg in messages:
        initial.append(
            {
                "prj_cd": msg.message.project_milestone.project.prj_cd,
                "prj_nm": msg.message.project_milestone.project.prj_nm,
                "msg": msg.message.msgtxt,
                "msg_id": msg.id,
                "user_id": msg.user.id,
                "url": msg.message.project_milestone.project.get_absolute_url(),
            }
        )

    return initial


def replace_links(text, link_patterns):
    """
    A little function that will replace string patterns in text with
    supplied hyperlinks.  'text' is just a string, most often a field
    in a django or flask model.  link_pattern is a list of two element
    dictionaries.  Each dicationary must have keys 'pattern' and
    'url'.  'pattern' is the regular expression to apply to the text
    while url is the text to be used as its replacement.  Regular
    expression call backs are supported.  See the python documentation
    for re.sub for more details.

    Note: The function does not make any attempt to validate the link or
    the regex pattern.

    """

    import re
    from markdown2 import markdown

    for pattern in link_patterns:
        regex = re.compile(pattern.get("pattern"), re.IGNORECASE)
        if "project:" in pattern.get("pattern"):
            # mark down replace _ with ems - replace them first:
            text = re.sub(r"</?em>", "_", text)
            prj_codes = regex.findall(text)
            for x in prj_codes:
                link = pattern["url"]
                href = link.format(x.lower(), x.upper())
                text = text.replace(x, href)
        else:
            text = re.sub(regex, pattern["url"], text)
    return text


def get_or_none(model, **kwargs):
    """
    from http://stackoverflow.com/questions/1512059/
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def group_required(*group_names):
    """
    Requires user membership in at least one of the groups passed in.
    """
    # from:http://djangosnippets.org/snippets/1703/
    def in_groups(user):
        """
        returns true if user is in one of the groups in group_names or is a
        superuser
        """
        if user.is_authenticated:
            if bool(user.groups.filter(name__in=group_names)) | user.is_superuser:
                return True
        return False

    return user_passes_test(in_groups)


def is_manager(user):
    """
    A simple little function to find out if the current user is a
    project tracker manager.
    """
    # this code uses Django groups, we want to use roles in Project Tracker Employee:
    # manager = False
    # if user:
    #     if user.groups.filter(name="manager").count() > 0 | user.is_superuser:
    #         manager = True
    #     # else:
    #     #    manager = False
    # return manager

    manager = False
    if hasattr(user, "employee"):
        manager = True if user.employee.role == "manager" else False
    return manager


def is_dba(user):
    """
    A simple little function to find out if the supplied user is a
    project tracker dba.
    """
    dba = False
    if hasattr(user, "employee"):
        dba = True if user.employee.role == "dba" else False
    return dba


def can_edit(user, project):
    """
    Another helper function to see if this user should be allowed
    to edit this project.  In order to edit the use must be either the
    project owner or lead, a manager, a superuser, a dba, or the field lead.
    """

    if project.is_complete():
        return False

    if user:
        canedit = (
            # (user.groups.filter(name="manager").count() > 0)
            (user.is_superuser)
            or (user == project.owner)
            or (user == project.field_ldr)
            or (is_dba(user))
            or (is_manager(user))
        )
    else:
        canedit = False

    if canedit:
        return True
    else:
        return False


def get_assignments_with_paths(project, core=True):
    """
    function that will return a list of dictionaries for each of the
    reporting requirements.  each dictionary will indicate what the
    report is, whether or not it has been requested for this
    project, and if it is available, a path to the associated
    report.
    """

    from ..models import Report

    if core:
        assignments = project.get_core_assignments()
    else:
        assignments = project.get_custom_assignments()

    assign_dicts = []
    for assignment in assignments:
        try:
            report = Report.objects.get(projectreport=assignment, current=True)
        except Report.DoesNotExist:
            report = None
        required = assignment.required
        milestone = assignment.milestone
        category = assignment.milestone.category
        assign_dicts.append(
            dict(
                required=required, category=category, milestone=milestone, report=report
            )
        )
    return assign_dicts


def update_milestones(form_ms, milestones):
    """
    a helper function to update milestones assocaited with a project.
    events that are in form_ms but have not been completed for this
    project will be updated with a time stamp, events associated with
    this project that are not in form_ms will have their time stamp
    cleared.

    + milestones - queryset of milestones associated with a project
        generated by proj.get_milestones()

    + forms_ms - list of projectmilestone id numbers generated from
        form.cleaned_data['milestones']

    """

    from ..models import ProjectMilestones

    # convert the list of milestones from the form to a set of integers:
    form_ms = set([int(x) for x in form_ms])

    old_completed = milestones.filter(completed__isnull=False)
    old_outstanding = milestones.filter(completed__isnull=True)

    old_completed = set([x.id for x in old_completed])
    old_outstanding = set([x.id for x in old_outstanding])

    now = datetime.datetime.now(pytz.utc)

    # these ones are now complete:
    added_ms = old_outstanding.intersection(form_ms)
    # ProjectMilestones.objects.filter(id__in=added_ms).update(completed=now)

    # in order to trigger a signal - we need to loop over each project
    # milestone, and mannually save them:
    for prjms_id in added_ms:
        prjms = ProjectMilestones.objects.get(id=prjms_id)
        prjms.completed = now
        prjms.save()

    # these ones were done, but now they aren't
    removed_ms = old_completed.difference(form_ms)
    # ProjectMilestones.objects.filter(id__in=removed_ms).update(completed=None)
    for prjms_id in removed_ms:
        prjms = ProjectMilestones.objects.get(id=prjms_id)
        prjms.completed = None
        prjms.save()


def get_sisters_dict(slug):
    """
    given a slug, return a list of dictionaries of projects that
    are (or could be) sisters to the given project.  Values returned
    by this function are used to populate the sister project formset
    """

    from ..models import Project

    project = get_object_or_404(Project, slug=slug)
    initial = []

    # family = project.get_family()
    sisters = project.get_sisters()
    candidates = project.get_sister_candidates()

    if sisters:
        for proj in sisters:
            initial.append(
                dict(
                    sister=True,
                    prj_cd=proj.prj_cd,
                    slug=proj.slug,
                    prj_nm=proj.prj_nm,
                    prj_ldr=proj.prj_ldr,
                    url=proj.get_absolute_url(),
                )
            )
    if candidates:
        for proj in candidates:
            initial.append(
                dict(
                    sister=False,
                    prj_cd=proj.prj_cd,
                    slug=proj.slug,
                    prj_nm=proj.prj_nm,
                    prj_ldr=proj.prj_ldr,
                    url=proj.get_absolute_url(),
                )
            )
    return initial


def make_proj_ms_dict(proj_ms, milestones):
    """

    # given a list of dictionaries containing project
    # milesstones return a dictionary keyed by project code that contains
    # the status of each milestone (represents a row in 'my projects table')


    Arguments:
    - `proj_ms`:
    """

    ms_dict = {}
    for ms in milestones:
        ms_dict[ms.label] = {
            "type": "report" if ms.report else "milestone",
            "required": False,
            "completed": False,
            "status": "notRequired-notDone",
        }

    # add an empty custom report
    ms_dict["custom"] = {
        "type": "report",
        "required": False,
        "completed": False,
        "status": "notRequired-notDone",
    }

    proj_ms_dict = {}

    for item in proj_ms:
        prj_cd = item.get("project__prj_cd")
        proj = proj_ms_dict.get(prj_cd)
        if proj is None:
            prj_attrs = {
                "prj_nm": item["project__prj_nm"],
                "year": item["project__year"],
                "slug": item["project__slug"],
                "prj_cd": item["project__prj_cd"],
                "prj_ldr": item["project__prj_ldr__username"],
                "prj_lead": "{} {}".format(
                    item["project__prj_ldr__first_name"],
                    item["project__prj_ldr__last_name"],
                ),
                "project_type": item["project__project_type__project_type"],
            }
            # add our empty milestone entries here. they will be updated on subsequent iterations:
            proj_ms_dict[prj_cd] = {"attrs": prj_attrs, "milestones": dict(ms_dict)}
        else:
            proj = proj_ms_dict.pop(prj_cd)
            # build a dictionary that contains the status of this milestone:
            status = {
                "type": "report" if item["milestone__report"] else "milestone",
                "required": item["required"],
                "completed": True if item["completed"] else False,
            }
            # add status code here - keep logic out of templates:
            if status["completed"] is True:
                if status["required"] is True:
                    status["status"] = "required-done"
                else:
                    status["status"] = "notRequired-done"
            else:
                if status["required"] is True:
                    status["status"] = "required-notDone"
                else:
                    status["status"] = "notRequired-notDone"
            # get the project milestones
            ms = proj.pop("milestones")

            # add our current mileone
            ms[item["milestone__label"]] = status
            proj["milestones"] = ms
            proj_ms_dict[prj_cd] = dict(proj)

    return proj_ms_dict


def get_projects_for_approval(year, this_year=True):
    # get projects_for_approval - returns a queryset containing the
    # project that are eligible for approval either this year, or last year.
    # we could filter here - lakes__in.

    from pjtk2.models import Project

    projects = Project.objects.filter(
        projectmilestones__milestone__label="Sign off",
        projectmilestones__completed__isnull=True,
        cancelled=False,
    )

    if this_year:
        return projects.filter(year__gte=year)
    else:
        return projects.filter(year=(year - 1))


def get_approve_project_dict(year, this_year=True):
    """
    Get the approve_projects_dict - takes a queryset that returns the
    list of active projects (not cancelled, not complete) and returns a dictionary
    that can be passed to the ApproveProjectForm.

    Arguments:
    - `projects`:
    """
    from pjtk2.models import ProjectMilestones

    projects = get_projects_for_approval(year, this_year)

    dictionary_list = (
        ProjectMilestones.objects.filter(
            project__in=Subquery(projects.values("pk")), milestone__label="Approved"
        )
        .select_related(
            "project",
            "project__prj_ldr",
            "project__project_type",
            "project__protocol",
            "project__lake",
        )
        .annotate(
            approved=Case(
                When(completed=None, then=False),
                default=True,
                output_field=BooleanField(),
            ),
            lake=F("project__lake__lake_name"),
            prj_cd=F("project__prj_cd"),
            prj_nm=F("project__prj_nm"),
            prj_ldr=F("project__prj_ldr__username"),
            prj_ldr_label=Concat(
                "project__prj_ldr__first_name",
                Value(" "),
                "project__prj_ldr__last_name",
            ),
            project_type=F("project__project_type__project_type"),
            protocol=F("project__protocol__protocol"),
        )
        .values(
            "id",
            "lake",
            "approved",
            "prj_cd",
            "prj_nm",
            "prj_ldr",
            "prj_ldr_label",
            "project_type",
            "protocol",
        )
    )
    return dictionary_list
