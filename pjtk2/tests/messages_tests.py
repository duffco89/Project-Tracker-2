'''These tests verify that the functions associated with the
noficiation system work as expected.  We can build an appropriate list
of recipients, we can send messages to all members of that list,
retreive both read and unread messages for a particular recipient and
send messages when pre_save and post_save signals are emitted by the
ProjectMilestones table.
'''

from django.test import TestCase

from pjtk2.models import *
from pjtk2.tests.factories import *


from pjtk2.views import get_messages_dict

import datetime
import pytz


def print_err(*args):
    sys.stderr.write(' '.join(map(str, args)) + '\n')


class TestBuildRecipientsList(TestCase):

    def setUp(self):
        '''Set up a fairly complicated employee heirachy with 6 employees'''

        self.user1 = UserFactory(first_name="Jerry", last_name="Seinfield",
                                 username='jseinfield')

        self.user2 = UserFactory(first_name="George", last_name="Costanza",
                                 username='gcostanza')

        self.user3 = UserFactory(first_name="Cosmo", last_name="Kramer",
                                 username='ckramer')
        self.user4 = UserFactory(first_name="Elaine", last_name="Benis",
                                 username='ebenis')
        self.user5 = UserFactory(first_name="Kenny", last_name="Banya",
                                 username='kbanya')

        self.user6 = UserFactory(first_name="Ruteger", last_name="Newman",
                                 username='rnewman')

        #bob sakamano is below the project owner and should not be notified.
        self.user7 = UserFactory(first_name="Bob", last_name="Sakamano",
                                 username='bsakamano')

        #now setup employee relationships
        #jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        #George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2,
                                         supervisor=self.employee1)
        #Kramer works for Jerry
        self.employee3 = EmployeeFactory(user=self.user3,
                                         supervisor=self.employee1)
        #Elaine works for Kramer
        self.employee4 = EmployeeFactory(user=self.user4,
                                         supervisor=self.employee3)
        #Banya also works for Kramer
        self.employee5 = EmployeeFactory(user=self.user5,
                                         supervisor=self.employee3)
        #Newman works for Banya
        self.employee6 = EmployeeFactory(user=self.user6,
                                         supervisor=self.employee5)
        #Bob Sakamano works for Newman
        self.employee7 = EmployeeFactory(user=self.user7,
                                         supervisor=self.employee6)

        #now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user6,
                                              dba=self.user2)

    def test_levels_null(self):
        '''by default, if no aguments are included, the message will be sent
        to everyone in the project hierarchy, including the DBA'''

        shouldbe = [self.user6, self.user5, self.user3,
                    self.user2, self.user1]

        #Elaine and bob are not directly in the employee heirachy
        #should_not_be = [self.user4, self.employee7]

        recipients = build_msg_recipients(self.project1)
        #compare what the funtion returns vs what we think it should.
        self.assertItemsEqual(recipients, shouldbe)

    def test_levels2(self):
        '''in this case we only want message to propegate up to the second
        level of the heirarchy - George and Jerry should not be on the DL.'''

        shouldbe = [self.user6, self.user5, self.user3, self.user2]

        #elaine is not directly in the employee heirachy and we don't
        #want the message to propegate up as high as Jerry.
        #should_not_be = [self.user1, self.user4]

        recipients = build_msg_recipients(self.project1, level=2)
        #compare what the funtion returns vs what we think it should.
        self.assertItemsEqual(recipients, shouldbe)

    def test_no_dba(self):
        '''Make sure that George is not on the DL if the dba option is set to
        False'''
        shouldbe = [self.user6, self.user5, self.user3, self.user1]

        #elaine, bob and george should not be included
        #should_not_be = [self.user2, self.user4, self.employee7]

        recipients = build_msg_recipients(self.project1, dba=False)
        #compare what the funtion returns vs what we think it should.
        self.assertItemsEqual(recipients, shouldbe)

    def test_watchers(self):
        '''Make sure that anyone who has bookmarked this project is also
        included in the DL'''

        #elaine is watching this project
        bookmark = Bookmark.objects.create(user=self.user4,
                                           project=self.project1)

        shouldbe = [self.user6, self.user5, self.user4,
                    self.user3, self.user2, self.user1]

        #bob is still on the sidelines
        #should_not_be =[self.employee7]

        recipients = build_msg_recipients(self.project1)
        #compare what the funtion returns vs what we think it should.
        self.assertItemsEqual(recipients, shouldbe)

    def test_watching_dba(self):
        '''if the dba is watching a project, make sure that he is in the list
        only once.'''

        #make a bookmark for george
        Bookmark.objects.create(user=self.user2,
                                           project=self.project1)

        shouldbe = [self.user6, self.user5,
                    self.user3, self.user2, self.user1]
        #should_not_be = [self.user4, self.employee7]

        recipients = build_msg_recipients(self.project1)
        #compare what the funtion returns vs what we think it should.
        self.assertItemsEqual(recipients, shouldbe)

    def test_ops(self):
        '''not implemented yet. - eventually, we would like to send a message
        to operations staff.'''
        pass

    def tearDown(self):

        self.project1.delete

        self.employee1.delete()
        self.employee2.delete()
        self.employee3.delete()
        self.employee4.delete()
        self.employee5.delete()
        self.employee6.delete()
        self.employee7.delete()

        self.user1.delete()
        self.user2.delete()
        self.user3.delete()
        self.user4.delete()
        self.user5.delete()
        self.user6.delete()
        self.user7.delete()


class TestSendMessages(TestCase):
    '''Some simple tests to verify that the functions associated with the
    messaging system function as expected.  send_messages should be able
    to send a simple message to a number of recipients.  my_messages()
    should be able to retrieve both read and unread messages for a
    particular user.
    '''

    def setUp(self):
        '''Set up a fairly complicated employee heirachy with 6 employees'''

        self.user1 = UserFactory(first_name="Jerry", last_name="Seinfield",
                                 username='jseinfield')

        self.user2 = UserFactory(first_name="George", last_name="Costanza",
                                 username='gcostanza')

        self.user3 = UserFactory(first_name="Cosmo", last_name="Kramer",
                                 username='ckramer')
        self.user4 = UserFactory(first_name="Elaine", last_name="Benis",
                                 username='ebenis')

        #now setup employee relationships
        #jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        #George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2,
                                         supervisor=self.employee1)
        #Kramer works for Jerry
        self.employee3 = EmployeeFactory(user=self.user3,
                                         supervisor=self.employee1)
        #Elaine works for Kramer
        self.employee4 = EmployeeFactory(user=self.user4,
                                         supervisor=self.employee3)

        #we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(label="Approved",
                                                  category='Core', order=1,
                                                  report=False)

        #now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user3,
                                              dba=self.user2)

    def test_send_messages(self):
        '''Verify that we can send a simple message to several people.'''

        #make sure the tables are empty
        messages = Message.objects.all().count()
        self.assertEqual(messages, 0)

        messages2users = Messages2Users.objects.all().count()
        self.assertEqual(messages, 0)

        #build the list of recipients
        send_to = [self.user1, self.user2, self.user3]
        msgtxt = "a fake message."

        send_message(msgtxt=msgtxt, recipients=send_to,
                     project=self.project1, milestone=self.milestone1)

        #verify that the message is in the message table
        messages = Message.objects.all()
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages[0].msg, msgtxt)

        #verify that there is a record in message2user for each recipient
        messages2users = Messages2Users.objects.all()
        self.assertEqual(messages2users.count(), 3)

    def test_my_messages(self):
        '''verify that the my_messages function can retrieve both read and
        unread messages associated with a user.'''

        send_to = [self.user1]

        msgtxt = ["the first message.", "the second message.",
                  "the third message.", "the fourth message."]

        for msg in msgtxt:
            send_message(msgtxt=msg, recipients=send_to,
                         project=self.project1, milestone=self.milestone1)

        #here is the orm way of getting the messages
        messages2users = Messages2Users.objects.filter(user=self.user1)
        #here is my function
        messages = my_messages(user=self.user1)
        #make sure they are equal
        self.assertEqual(messages2users.count(), messages.count())

        #the messages should be returned in reverse chronological order
        msgtxt.reverse()
        self.assertQuerysetEqual(messages, msgtxt,
                                 lambda a: a.msg.msg)

        #say the first and second messages were read
        Messages2Users.objects.filter(msg__id__in=[1, 2]).update(
            read=datetime.datetime.now(pytz.utc))

        #now when we call messages we should only see the unread messages
        messages = my_messages(user=self.user1)

        #make sure the expect number are returned
        self.assertEqual(messages.count(), 2)
        #the unread messages should be returned in reverse chronological order
        self.assertQuerysetEqual(messages, msgtxt[:2],
                                 lambda a: a.msg.msg)

        #if we pass in the only_unread=False, we should get them all
        messages = my_messages(user=self.user1, only_unread=False)

        #make sure it returns the number of records we think it does
        self.assertEqual(messages.count(), 4)
        #the messages should be returned in reverse chronological order
        self.assertQuerysetEqual(messages, msgtxt,
                                 lambda a: a.msg.msg)

    def tearDown(self):
        self.project1.delete()
        self.milestone1.delete()

        self.employee1.delete()
        self.employee2.delete()
        self.employee3.delete()
        self.employee4.delete()

        self.user1.delete()
        self.user2.delete()
        self.user3.delete()
        self.user4.delete()


class TestSendNoticeWhenProjectMilestonesChange(TestCase):
    '''Verify that when project milestones are updated, messages are sent
    to the project lead, their supervisor and the dba.'''

    def setUp(self):
        '''for these tests, we need a project, some milestones, a project
        lead, a supervisor and a dba'''

        self.user1 = UserFactory(first_name="Jerry", last_name="Seinfield",
                                 username='jseinfield')

        self.user2 = UserFactory(first_name="George", last_name="Costanza",
                                 username='gcostanza')

        self.user3 = UserFactory(first_name="Cosmo", last_name="Kramer",
                                 username='ckramer')

        #now setup employee relationships
        #jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        #George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2,
                                         supervisor=self.employee1)
        #Kramer works for Jerry
        self.employee3 = EmployeeFactory(user=self.user3,
                                         supervisor=self.employee1)

        #we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(label="Submitted",
                                                  category='Core', order=1,
                                                  report=False)

        self.milestone2 = MilestoneFactory.create(label="Approved",
                                                  category='Core', order=2,
                                                  report=False)

        #we need a milestone to associate the message with
        #self.milestone3 = MilestoneFactory.create(label='Completed',
        #                                          category='Core', order=3,
        #                                          report=False)

        #now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user3,
                                              dba=self.user2)

    def test_send_message_project_approved(self):
        '''When Jerry approves the project, Jerry, George and Kramer should
        all get a message stating that.'''

        Jerrys_msgs = my_messages(self.user1)
        Georges_msgs = my_messages(self.user2)
        Kramers_msgs = my_messages(self.user3)

        self.assertEqual(Jerrys_msgs.count(), 1)
        self.assertEqual(Georges_msgs.count(), 1)
        self.assertEqual(Kramers_msgs.count(), 1)

        self.project1.approve()

        Jerrys_msgs = my_messages(self.user1)
        Georges_msgs = my_messages(self.user2)
        Kramers_msgs = my_messages(self.user3)

        self.assertEqual(Georges_msgs.count(), 2)
        self.assertEqual(Jerrys_msgs.count(), 2)
        self.assertEqual(Kramers_msgs.count(), 2)

        #check on of the users to verify that they message they
        #recieve is what you think it should be:
        self.assertEqual(Georges_msgs[0].msg.msg, 'Approved')
        self.assertEqual(Georges_msgs[1].msg.msg, 'Submitted')

    def test_send_message_project_unapproved(self):
        '''If a project is approved and subsquently un-approved, the project
        lead should get a meaningful message for each event.'''

        #approve the project
        self.project1.approve()
        #immediately unapprove it
        self.project1.unapprove()

        Georges_msgs = my_messages(self.user2)

        for msg in Georges_msgs:
            print msg.msg

        self.assertEqual(Georges_msgs.count(), 3)

        #check on of the users to verify that they message they
        #recieve is what you think it should be:
        msgtxt = "The milestone 'Approved' has been revoked"
        self.assertEqual(Georges_msgs[0].msg.msg, msgtxt)
        self.assertEqual(Georges_msgs[1].msg.msg, 'Approved')
        self.assertEqual(Georges_msgs[2].msg.msg, 'Submitted')

    def tearDown(self):

        self.project1.delete()
        self.milestone1.delete()
        self.milestone2.delete()

        self.employee1.delete()
        self.employee2.delete()
        self.employee3.delete()

        self.user1.delete()
        self.user2.delete()
        self.user3.delete()


class TestGetMessagesDict(TestCase):
    '''This tests that the function that bundles the notification
    information into a dictionary works as it should.

    '''

    def setUp(self):
        '''for these tests, we need a project, some milestones, a project
        lead, a supervisor and a dba'''

        self.user1 = UserFactory(first_name="Jerry", last_name="Seinfield",
                                 username='jseinfield')

        #now setup employee relationships
        #jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)

        #we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(label="Submitted",
                                                  category='Core', order=1,
                                                  report=False)

        self.milestone2 = MilestoneFactory.create(label="Approved",
                                                  category='Core', order=2,
                                                  report=False)

        #now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user1)


    def test_messages_dict(self):
        '''Verify that the information returned by message_dict are the same
        as their inputs'''

        #get the messages for our user
        messages = my_messages(self.user1)
        #get the dictionary which include project, user and message info
        msg_dict = get_messages_dict(messages)
        self.assertEqual(len(msg_dict), 1)

        self.assertEqual(msg_dict[0]['user_id'], self.user1.id)
        self.assertEqual(msg_dict[0]['url'], self.project1.get_absolute_url())
        self.assertEqual(msg_dict[0]['prj_cd'], self.project1.prj_cd)
        self.assertEqual(msg_dict[0]['prj_nm'], self.project1.prj_nm)
        self.assertEqual(msg_dict[0]['msg_id'], messages[0].id)

        #approve the project to create a new message
        self.project1.approve()

        #we should have two messages now
        messages = my_messages(self.user1)
        msg_dict = get_messages_dict(messages)
        self.assertEqual(len(msg_dict), 2)

        self.assertEqual(msg_dict[0]['user_id'], self.user1.id)
        self.assertEqual(msg_dict[0]['url'], self.project1.get_absolute_url())
        self.assertEqual(msg_dict[0]['prj_cd'], self.project1.prj_cd)
        self.assertEqual(msg_dict[0]['prj_nm'], self.project1.prj_nm)
        self.assertEqual(msg_dict[0]['msg_id'], messages[0].id)
        #verify that the msg_id is correct
        self.assertEqual(msg_dict[1]['msg_id'], messages[1].id)


        #print msg_dict
        #assert 1==0





















