'''This file contains a number of helper functions.  Most of the
functions are used in views.py,but they are not views themselves.'''



## from pjtk2.models import (Milestone, Project, Report, ProjectReports,
##                           ProjectType, Database, Bookmark, ProjectSisters, 
##                           Family, employee)
## 


def get_supervisors(employee):
    '''Given an employee object, return a list of supervisors.  the first
    element of list will be the intial employee.'''
    if employee.supervisor:
        return [employee] + get_supervisors(employee.supervisor)
    else:
        return [employee]

def get_minions(employee):
    '''Given an employee objects, return a list of employees under
    his/her## from pjtk2.models import (Milestone, Project, Report,
    ProjectReports, supervision.  The first element of list will be
    the intial employee.

    '''
    ret=[employee]
    for minion in employee.employee_set.all():
        #ret.append(get_minions(minion))        
        ret.extend(get_minions(minion))
    return ret


def is_manager(user):
    '''A simple little function to find out if the current user is a
    manager (or better)'''
    if user.groups.filter(name='manager').count()>0 | user.is_superuser:
        manager = True
    else:
        manager = False
    return(manager)

def canEdit(user, project):
    '''Another helper function to see if this user should be allowed
    to edit this project.  In order to edit the use must be either the
    project Owner, a manager or a superuser.'''
    canEdit = ((user.groups.filter(name='manager').count()>0) or
                 (user.is_superuser) or
                 (user.username == project.owner.username))
    if canEdit:
        canEdit = True
    else:
        canEdit = False
    return(canEdit)


def get_assignments_with_paths(slug, Core=True):
    '''function that will return a list of dictionaries for each of the
    reporting requirements.  each dictionary will indicate what the
    report is required, whether or not it has been requested for this
    project, and if it is available, a path to the associated
    report.'''

    project = Project.objects.get(slug=slug)

    if Core:
        assignments = project.get_core_assignments()
    else:
        assignments = project.get_custom_assignments()

    assign_dicts = []
    for assignment in assignments:
        try:
            filepath = Report.objects.get(projectreport=assignment, current=True)
        except Report.DoesNotExist:
            filepath = None
        required = assignment.required
        report_type = assignment.report_type
        category = assignment.report_type.category
        assign_dicts.append(dict(
            required = required,
            category = category,
            report_type = report_type,
            filepath = filepath
        ))
    return assign_dicts



## def sendMessage(msgtxt, users, project, milestone):
## 
##     '''Create a record in the message database and send it to each user in
##     users by appending a record to Messages2Users for each one.'''
## 
##     #if the Project Milestone doesn't exist for this project and milestone create it
##     prjms, created = ProjectMilestones.objects.get_or_create(project=project, 
##                                                              milestone=milestone)
## 
##     #create a message object using the message text and the project-milestone
##     message = Message.objects.create(msg=msgtxt, ProjectMilestone=prjms)
##     #then loop through the list of users and add one record to 
##     #Messages2Users for each one:
##     try:
##         for user in users:
##             Messages2Users.objects.create(user=user, msg=message)
##     except TypeError:
##         Messages2Users.objects.create(user=users, msg=message)
## 
## 
## def myMessages(user, OnlyUnread=True):
##     '''Return a queryset of messages for the user, sorted in reverse
##     chronilogical order (newest first).  By default, only unread messages
##     are returned, but all messages can be retrieved.'''
## 
##     if OnlyUnread:
##          MyMsgs = Messages2Users.objects.filter(user=user, 
##                                                 read__isnull=True).order_by('-created')
##     else:
##          MyMsgs = Messages2Users.objects.filter(user=user).order_by('-created')
##     return(MyMsgs)
