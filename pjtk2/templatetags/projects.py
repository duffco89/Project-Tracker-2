from django import template
from pjtk2.models import Project, Bookmark

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
