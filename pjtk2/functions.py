'''This file contains a number of helper functions.  Most of the
functions are used in views.py,but they are not views themselves.'''



def get_supervisors(employee):
    '''Given an employee object, return a list of supervisors.  the first
    element of list will be the intial employee.'''
    if employee.supervisor:
        return [employee] + get_supervisors(employee.supervisor)
    else:
        return [employee]


def get_minions(employee):
    '''Given an employee objects, return a list of employees under his/her
    supervision.  The first element of list will be the intial
    employee.
    '''
    ret = [employee]
    for minion in employee.employee_set.all():
        #ret.append(get_minions(minion))
        ret.extend(get_minions(minion))
    return ret


def my_messages(user, only_unread=True):
    '''Return a queryset of messages for the user, sorted in reverse
    chronological order (newest first).  By default, only unread messages
    are returned, but all messages can be retrieved.'''

    from pjtk2.models import Messages2Users

    if only_unread:
        my_msgs = (Messages2Users.objects.filter(user=user,
                            read__isnull=True).order_by('-created'))
    else:
        my_msgs = Messages2Users.objects.filter(user=user).order_by('-created')
    return(my_msgs)


def get_messages_dict(messages):
    '''given  notification message, pull out the project, url, id and
    message.  wrap them up in a dict and return it.  The dict is then
    passed to the notifcation form so that each message can be displayed
    and marked as read by the user.'''

    initial = []

    for msg in messages:
        initial.append({
            'prj_cd': msg.msg.project_milestone.project.prj_cd,
            'prj_nm': msg.msg.project_milestone.project.prj_nm,
            'msg': msg.msg.msg,
            'msg_id': msg.id,
            'user_id': msg.user.id,
            'url': msg.msg.project_milestone.project.get_absolute_url(),
        })

    return initial







