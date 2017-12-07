from django import template
from django.conf import settings
from pjtk2.models import Project, Bookmark, ProjectType, Milestone

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



@register.filter
def fisheye_button(project):
    '''a template filter to return a bootstrap styled button link to the
    project detail page in fisheye, fsis-ii or the creel portal.
    Controlled by the values in LOCAL_LINKS in settings/base.py

    The LOCAL_LINKS contains the base ip address were the other apps
    are being hosted, followed by a series of dictionaries - one for
    each proejct type.  The project dictionaries contain these elements:

    - port : the port the application is listening on

    - detail_url : the url that contain the detail view we want to access

    - button_label: the label that will appear on the rendered button

    - identifier: the name of the field that when combined with detail
      url, returns the appropriate detail view.  Usually this is
      'slug', but inthe case of fish stocking is 'year'

    - if local links can't be found or the project type is not in the
      list of projects included in local links, the function retuns an
      empty string.

    '''
    local_links = settings.LOCAL_LINKS
    if local_links is None:
        return ""
    else:
        merged = Milestone.objects.filter(label='Data Merged').first()
        if merged is None:
            return ""
        else:
            project_type = project.project_type.project_type
            project_vals = local_links.get('project_types').get(project_type)

            if project_vals and project.milestone_complete(merged):
                project_vals['ipaddress'] = local_links.get('ipaddress')
                project_vals['id_val'] = getattr(project,
                                                 project_vals.get('identifier'))
                url = "http://{ipaddress}:{port}/{detail_url}/{id_val}".\
                      format(**project_vals)
                link = '<a class="btn btn-primary" href="{}" role="button">{}</a>'
                link = link.format(url, project_vals['button_label'])
                return mark_safe(link)
            else:
                return ""
