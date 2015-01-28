from django import template
from pjtk2.models import Project, Bookmark

from django.template.defaultfilters import stringfilter
#from django.contrib.auth import user
from django.utils.safestring import mark_safe

register = template.Library()


def do_if_Bookmarked(parser, token):
    '''modified from PracticalDjangoProjects (page 193)'''
    bits = token.contents.split()
    if len(bits) !=3:
        raise template.TemplateSyntaxError(
            "%s tag takes two arguments" % bits[0])
    nodelist_true = parser.parse(('else', 'endif_bookmarked'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif_bookmarked',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return IfBookmarkedNode(bits[1], bits[2], nodelist_true, nodelist_false)


class IfBookmarkedNode(template.Node):
    def __init__(self, user, project, nodelist_true, nodelist_false):
        self.nodelist_false = nodelist_false
        self.nodelist_true = nodelist_true
        self.user = template.Variable(user)
        self.project = template.Variable(project)

    def render(self, context):
        try:
            user = self.user.resolve(context)
            project = self.project.resolve(context)
        except template.VariableDoesNotExist:
            return ""
        if Bookmark.objects.filter(user__pk=user.id,
                                  project__slug=project.slug):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


register = template.Library()
register.tag("if_bookmarked", do_if_Bookmarked)



@register.filter
def milestone_status(project, reports):
    ''' The milestone_status template tag takes a project and a list of core
    reports and returns glyph icons for completed, missing, and not required
    milestones.  Each glyph is wrapped in table data elements so that they
    can be directly integrated into summary report table.
    '''

    html = ""

    for report in reports:
        status = project.milestone_complete(report)
        if status == False:
            glyph = '<span class="glyphicon glyphicon-question-sign icon-red"></span>'
        elif status==True:
            glyph = '<span class="glyphicon glyphicon-ok icon-green"></span>'
        else:
            glyph = '<span class="glyphicon glyphicon-minus icon-grey"></span>'

        html += "<td>{0}</td>\n".format(glyph)

    return mark_safe(html)


@register.filter
def highlight_status(status):
    ''' a little filter to colour our status entires in project lists.
    '''

    if status == 'Cancelled':
        return 'red'
    elif status == 'Ongoing':
        return 'blue'
    elif status == 'Complete':
        return 'green'
    else:
        return 'black'
