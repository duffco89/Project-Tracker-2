from django.core.urlresolvers import reverse
from django_webtest import WebTest
#from testfixtures import compare
from pjtk2.tests.factories import *
from pjtk2.models import Bookmark



class BookmarkTestCase(WebTest):

    def setUp(self):
        ''' '''
        
        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')
       
        self.ProjType = ProjTypeFactory(Project_Type = "Nearshore Index")
        
        self.project = ProjectFactory.create(PRJ_CD="LHA_IA12_111", YEAR=2012, 
                                              Owner=self.user, slug='lha_ia12_111',
                                              ProjectType = self.ProjType)
    csrf_checks = False   
    def test_add_delete_bookmarks(self):

        #make sure that we are starting out without any bookmarks
        bookmarkcnt = Bookmark.objects.filter(user__pk=self.user.id).count()
        self.assertEqual(bookmarkcnt, 0)

        #==================
        #   ADD BOOKMARK
        #a request to bookmark should add a bookmark
        response = self.app.get(reverse('Bookmark_Project', 
                                args=(self.project.slug,)), user=self.user)
        self.assertEqual(response.status_int, 302)
        bookmarkcnt = Bookmark.objects.filter(user__pk=self.user.id).count()
        self.assertEqual(bookmarkcnt, 1)
        #make sure the bookmark is the one we think it is:
        bookmark = Bookmark.objects.get(user__pk=self.user.id)
        self.assertEqual(bookmark.get_project_code(), self.project.PRJ_CD)

        #==================
        #  CONFIRM DELETE
        #check that the a get request to unbookmark produce the confirm page
        response = self.app.get(reverse('Unbookmark_Project', 
                                args=(self.project.slug,)), user=self.user)
        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed(response, 'confirm_bookmark_delete.html')

        #==================
        #  DELETE BOOKMARK
        #check that the post request really does delete the bookmark
        response = self.app.post(reverse('Unbookmark_Project', 
                                args=(self.project.slug,)), user=self.user)
        self.assertEqual(response.status_int, 302)
        bookmarkcnt = Bookmark.objects.filter(user__pk=self.user.id).count()
        self.assertEqual(bookmarkcnt, 0)
