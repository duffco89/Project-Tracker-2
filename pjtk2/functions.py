'''This file contains a number of helper functions.  Most of the
functions are used in views.py,but they are not views themselves.'''

import re


def strip_carriage_returns(my_string):
    """A little helper function to remove carriage returns from text.
    This function is intended to help with artifacts introduced by cutting
    and pasting from word - if people do that, carriage returns are added
    to end of each line.  This fucntion removes those carriage returns
    without disrupting the paragraph structure or markdown.

    Arguments: - `my_string`: the string from which to remove
    extranious carriage returns.

    """

    if my_string is None:
        return None

    my_lines = my_string.splitlines()
    for i, x in enumerate(my_lines):
        if x=='' or re.match('\s', x):
            my_lines[i] = "\r\n\r\n"
        else:
            my_lines[i] +=" "
    return "".join(my_lines).strip()




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


def my_messages(user, all=False):
    '''Return a queryset of messages for the user, sorted in reverse
    chronological order (newest first).  By default, only unread messages
    are returned, but all messages can be retrieved.'''

    from pjtk2.models import Messages2Users

    my_msgs = Messages2Users.objects.filter(user=user)\
                                    .select_related('user',
                                                    'message__project_milestone',
                                                    'message__project_milestone__project')\
                                    .order_by('-created')
    if not all:
        my_msgs = my_msgs.filter(read__isnull=True)

    return(my_msgs)


def get_messages_dict(messages):
    '''given  notification message, pull out the project, url, id and
    message.  wrap them up in a dict and return it.  The dict is then
    passed to the notifcation form so that each message can be displayed
    and marked as read by the user.

    messages is a list of Messages2Users objects
'''

    initial = []

    for msg in messages:
        initial.append({
            'prj_cd': msg.message.project_milestone.project.prj_cd,
            'prj_nm': msg.message.project_milestone.project.prj_nm,
            'msg': msg.message.msgtxt,
            'msg_id': msg.id,
            'user_id': msg.user.id,
            'url': msg.message.project_milestone.project.get_absolute_url(),
        })

    return initial





def replace_links(text, link_patterns):
    """a little function that will replace string patterns in text with
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
        regex = re.compile(pattern.get('pattern'), re.IGNORECASE)
        if 'project:' in pattern.get('pattern'):
            #mark down replace _ with ems - replace them first:
            text = re.sub(r'</?em>', '_', text)
            prj_codes = regex.findall(text)
            for x in prj_codes:
                link = pattern['url']
                href = link.format(x.lower(), x.upper())
                text = text.replace(x,href)
        else:
            text = re.sub(regex, pattern['url'], text)
    return text
