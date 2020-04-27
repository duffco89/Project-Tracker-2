"""These verify that the functions associated with the
noficiation system work as expected.  We can build an appropriate list
of recipients, we can send messages to all members of that list,
retreive both read and unread messages for a particular recipient and
send messages when pre_save and post_save signals are emitted by the
ProjectMilestones table.
"""

import datetime
import pytz
import time

from django.test import TestCase

from pjtk2.models import *
from pjtk2.tests.factories import *
from pjtk2.utils.helpers import my_messages, get_messages_dict

from django.db.models.signals import pre_save, post_save

import pytest


@pytest.fixture(scope="module", autouse=True)
def connect_signals():
    """make sure to connect the signals before each test - they are needed
    here"""
    pre_save.connect(send_notice_prjms_changed, sender=ProjectMilestones)


def print_err(*args):
    sys.stderr.write(" ".join(map(str, args)) + "\n")


class TestMarkMessages(TestCase):
    """This testcase is intended to test the function mark_as_read()
    method of message2user objects.  When mark_as_read() is called on
    a messages2users object, the field [read] should be updated with a
    timestamp.
    """

    def setUp(self):
        """Create a user and end them 4 messages - two of which will be read"""

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Approved", category="Core", order=1, report=False
        )

        # now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(
            prj_cd="LHA_IA12_111", prj_ldr=self.user1, owner=self.user1, dba=self.user1
        )

        self.pms = self.project1.get_milestones()[0]

    def test_mark_messages_as_read(self):
        """A message is marked as read if the field [read] contains a time
        stamp. So, create some messages, verify that they aren't read,
        mark two as read using our method and verify that they have a
        time stamp.

        """

        msgtxt = [
            "the first message.",
            "the second message.",
            "the third message.",
            "the fourth message.",
        ]

        for txt in msgtxt:
            message = Message(msgtxt=txt, project_milestone=self.pms)
            message.save()
            msg4u = Messages2Users(user=self.user1, message=message)
            msg4u.save()

        messages = my_messages(user=self.user1)
        self.assertEqual(messages.count(), 4)

        messages[0].mark_as_read()
        messages[1].mark_as_read()

        # orm way of getting messges
        foo = Messages2Users.objects.filter(user=self.user1).order_by("read")

        # if mark_as_read works, the first two elements should contain
        # something, the last two will still be empty
        should_be = [False, False, True, True]
        self.assertQuerysetEqual(foo, should_be, lambda a: a.read is None)

    def tearDown(self):
        self.project1.delete()
        self.milestone1.delete()

        self.user1.delete()


class TestBuildRecipientsList(TestCase):
    """We want messages to propegate up the employee heirachy and be send
    to the dba and anyone who happens to be watching a project.  This
    test case verifies that messages are propegated properly and are
    not sent to people who don't need them.
    """

    def setUp(self):
        """Set up a fairly complicated employee heirachy with 6 employees"""

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        self.user3 = UserFactory(
            first_name="Cosmo", last_name="Kramer", username="ckramer"
        )
        self.user4 = UserFactory(
            first_name="Elaine", last_name="Benis", username="ebenis"
        )
        self.user5 = UserFactory(
            first_name="Kenny", last_name="Banya", username="kbanya"
        )

        self.user6 = UserFactory(
            first_name="Ruteger", last_name="Newman", username="rnewman"
        )

        # bob sakamano is below the project owner and should not be notified.
        self.user7 = UserFactory(
            first_name="Bob", last_name="Sakamano", username="bsakamano"
        )

        # now setup employee relationships
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        # George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2, supervisor=self.employee1)
        # Kramer works for Jerry
        self.employee3 = EmployeeFactory(user=self.user3, supervisor=self.employee1)
        # Elaine works for Kramer
        self.employee4 = EmployeeFactory(user=self.user4, supervisor=self.employee3)
        # Banya also works for Kramer
        self.employee5 = EmployeeFactory(user=self.user5, supervisor=self.employee3)
        # Newman works for Banya
        self.employee6 = EmployeeFactory(user=self.user6, supervisor=self.employee5)
        # Bob Sakamano works for Newman
        self.employee7 = EmployeeFactory(user=self.user7, supervisor=self.employee6)

        # now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(
            prj_cd="LHA_IA12_111", owner=self.user6, dba=self.user2
        )

    def test_levels_null(self):
        """by default, if no aguments are included, the message will be sent
        to everyone in the project hierarchy, including the DBA"""

        shouldbe = [self.user6, self.user5, self.user3, self.user2, self.user1]

        # Elaine and bob are not directly in the employee heirachy
        # should_not_be = [self.user4, self.employee7]

        recipients = build_msg_recipients(self.project1)
        # compare what the funtion returns vs what we think it should.
        self.assertCountEqual(recipients, shouldbe)

    def test_levels2(self):
        """in this case we only want message to propegate up to the second
        level of the heirarchy - George and Jerry should not be on the DL."""

        shouldbe = [self.user6, self.user5, self.user3, self.user2]

        # elaine is not directly in the employee heirachy and we don't
        # want the message to propegate up as high as Jerry.
        # should_not_be = [self.user1, self.user4]

        recipients = build_msg_recipients(self.project1, level=2)
        # compare what the funtion returns vs what we think it should.
        self.assertCountEqual(recipients, shouldbe)

    def test_no_dba(self):
        """Make sure that George is not on the DL if the dba option is set to
        False"""
        shouldbe = [self.user6, self.user5, self.user3, self.user1]

        # elaine, bob and george should not be included
        # should_not_be = [self.user2, self.user4, self.employee7]

        recipients = build_msg_recipients(self.project1, dba=False)
        # compare what the funtion returns vs what we think it should.
        self.assertCountEqual(recipients, shouldbe)

    def test_watchers(self):
        """Make sure that anyone who has bookmarked this project is also
        included in the DL"""

        # elaine is watching this project
        bookmark = Bookmark.objects.create(user=self.user4, project=self.project1)

        shouldbe = [
            self.user6,
            self.user5,
            self.user4,
            self.user3,
            self.user2,
            self.user1,
        ]

        # bob is still on the sidelines
        # should_not_be =[self.employee7]

        recipients = build_msg_recipients(self.project1)
        # compare what the funtion returns vs what we think it should.
        self.assertCountEqual(recipients, shouldbe)

    def test_watching_dba(self):
        """if the dba is watching a project, make sure that he is in the list
        only once."""

        # make a bookmark for george
        Bookmark.objects.create(user=self.user2, project=self.project1)

        shouldbe = [self.user6, self.user5, self.user3, self.user2, self.user1]
        # should_not_be = [self.user4, self.employee7]

        recipients = build_msg_recipients(self.project1)
        # compare what the funtion returns vs what we think it should.
        self.assertCountEqual(recipients, shouldbe)

    def test_ops(self):
        """not implemented yet. - eventually, we would like to send a message
        to operations staff."""
        pass

    def tearDown(self):

        self.project1.delete()

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
    """Some simple tests to verify that the functions associated with the
    messaging system function as expected.  send_messages should be able
    to send a simple message to a number of recipients.
    """

    def setUp(self):
        """Set up a fairly complicated employee heirachy with 6 employees"""

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        self.user3 = UserFactory(
            first_name="Cosmo", last_name="Kramer", username="ckramer"
        )
        self.user4 = UserFactory(
            first_name="Elaine", last_name="Benis", username="ebenis"
        )

        # now setup employee relationships
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        # George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2, supervisor=self.employee1)
        # Kramer works for Jerry
        self.employee3 = EmployeeFactory(user=self.user3, supervisor=self.employee1)
        # Elaine works for Kramer
        self.employee4 = EmployeeFactory(user=self.user4, supervisor=self.employee3)

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Approved", category="Core", order=1, report=False
        )

        # now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(
            prj_cd="LHA_IA12_111", prj_ldr=self.user3, owner=self.user3, dba=self.user2
        )

    def test_send_messages(self):
        """Verify that we can send a simple message to several people."""

        # make sure the tables are empty
        messages = Message.objects.all().count()
        self.assertEqual(messages, 0)

        messages2users = Messages2Users.objects.all().count()
        self.assertEqual(messages, 0)

        # build the list of recipients
        send_to = [self.user1, self.user2, self.user3]
        msgtxt = "a fake message."

        send_message(
            msgtxt=msgtxt,
            recipients=send_to,
            project=self.project1,
            milestone=self.milestone1,
        )

        # verify that the message is in the message table
        messages = Message.objects.all()
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages[0].msgtxt, msgtxt)

        # verify that there is a record in message2user for each recipient
        messages2users = Messages2Users.objects.all()
        self.assertEqual(messages2users.count(), 3)

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


class TestMyMessages(TestCase):
    """The helper function my_messages accepts a user and returns all of
    the Messages2Users objects associated with that user. my_messages()
    should be able to retrieve both read and unread messages for a
    particular user.
    """

    def setUp(self):
        """we will need two users, a project, a project milestone, and four
        messages.

        """

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        # now setup employee relationships
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        # George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2, supervisor=self.employee1)

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Submitted", category="Core", order=1, report=False
        )

        # now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(
            prj_cd="LHA_IA12_111", prj_ldr=self.user1, owner=self.user1, dba=self.user1
        )

        pms = self.project1.get_milestones()[0]

        self.msgtxt = [
            "the first message.",
            "the second message.",
            "the third message.",
            "the fourth message.",
        ]

        now = datetime.datetime.now(pytz.utc)
        # now = datetime.datetime.utcnow()
        read = [now, now, None, None]

        # create 4 messages and 4 message2user objects - two of the
        # message2user objects will have a time stamp.
        for txt, ts in zip(self.msgtxt, read):
            message = Message(msgtxt=txt, project_milestone=pms)
            message.save()
            msg4u = Messages2Users(user=self.user1, message=message, read=ts)
            msg4u.save()

    def test_my_messages_only_unread(self):
        """by default, my_messages should only include those messages that
        have not been read yet (i.e. [read] is null)"""

        msgs = my_messages(self.user1)
        # self.assertCountEqual(msgs, self.msgtxt[2:])
        should_be = self.msgtxt[2:]
        should_be.reverse()
        should_be.extend(["Submitted"])

        self.assertQuerysetEqual(msgs, should_be, lambda a: str(a.message.msgtxt))

    def test_my_messages_all(self):
        """We may want to see all of the messages that have been sent to a
        user, verify that we get them."""

        msgs = my_messages(self.user1, all=True)

        should_be = self.msgtxt
        should_be.reverse()
        should_be.extend(["Submitted"])

        self.assertQuerysetEqual(msgs, should_be, lambda a: str(a.message.msgtxt))

    def test_my_messages_no_messages(self):
        """If there aren't any messages for this user, return an empty list
        (gracefully)"""

        msgs = my_messages(self.user2)
        self.assertCountEqual(msgs, [])

    def tearDown(self):
        self.project1.delete()
        self.milestone1.delete()

        self.employee1.delete()
        self.employee2.delete()

        self.user1.delete()
        self.user2.delete()


class TestSendNoticeWhenProjectMilestonesChange(TestCase):
    """Verify that when project milestones are updated, messages are sent
    to the project lead, their supervisor and the dba."""

    def setUp(self):
        """for these tests, we need a project, some milestones, a project
        lead, a supervisor and a dba"""

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        self.user3 = UserFactory(
            first_name="Cosmo", last_name="Kramer", username="ckramer"
        )

        # now setup employee relationships
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        # George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2, supervisor=self.employee1)
        # Kramer works for Jerry
        self.employee3 = EmployeeFactory(user=self.user3, supervisor=self.employee1)

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Submitted", category="Core", order=1, report=False
        )

        self.milestone2 = MilestoneFactory.create(
            label="Approved", category="Core", order=2, report=False
        )

        # now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(
            prj_cd="LHA_IA12_111", owner=self.user3, dba=self.user2
        )

    def test_send_message_project_approved(self):
        """When Jerry approves the project, Jerry, George and Kramer should
        all get a message stating that."""

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

        # check on of the users to verify that they message they
        # recieve is what you think it should be:
        self.assertEqual(Georges_msgs[0].message.msgtxt, "Approved")
        self.assertEqual(Georges_msgs[1].message.msgtxt, "Submitted")

    def test_send_message_project_unapproved(self):
        """If a project is approved and subsquently un-approved, the project
        lead should get a meaningful message for each event."""

        # approve the project
        self.project1.approve()
        # immediately unapprove it
        self.project1.unapprove()

        Georges_msgs = my_messages(self.user2)

        for msg in Georges_msgs:
            print(msg.message)

        self.assertEqual(Georges_msgs.count(), 3)

        # check on of the users to verify that they message they
        # recieve is what you think it should be:
        msgtxt = "The milestone 'Approved' has been revoked"
        self.assertEqual(Georges_msgs[0].message.msgtxt, msgtxt)
        self.assertEqual(Georges_msgs[1].message.msgtxt, "Approved")
        self.assertEqual(Georges_msgs[2].message.msgtxt, "Submitted")

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
    """This tests that the function that bundles the notification
    information into a dictionary works as it should (this test might
    be a good candidate for mock objects - the setup seems harder than
    the tests).

    The first test is pretty simple - create a user and a project.
    Veryify that the messages dictionary contains information about it
    being submitted, and then approved after the project is approved.

    The second test is to verify that the function works properly when
    the messages for a give user are not contiguous.  THere was an
    earlier bug in the code that was caused by an incorrect reference
    to message.id (rather than message2user.id).  The first test will
    still pass because there is a one-to-one relationship in this
    simple case.  The second test creates a many-to-one situation and
    verifies that the correct messages are still being returned.

    """

    def setUp(self):
        """for these tests, we need a project, some milestones, a project
        lead, a supervisor and a dba"""

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        # There are no employee relationships.
        # george has no boss
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        self.employee2 = EmployeeFactory(user=self.user2)

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Submitted", category="Core", order=1, report=False
        )

        self.milestone2 = MilestoneFactory.create(
            label="Approved", category="Core", order=2, report=False
        )

        self.milestone3 = MilestoneFactory.create(
            label="Notice", category="Core", order=3, report=False
        )

        MilestoneFactory(label="Sign Off")

        # now create a project owned by jerry - nothing to do with george
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111", owner=self.user1)

        # now create a project owned by george - nothing to do with jerry
        self.project2 = ProjectFactory.create(prj_cd="LHA_IA12_999", owner=self.user2)

    def test_messages_dict(self):
        """Verify that the information returned by message_dict are the same
        as their inputs"""

        # get the messages for our user
        messages = my_messages(self.user1)
        # get the dictionary which include project, user and message info
        msg_dict = get_messages_dict(messages)
        self.assertEqual(len(msg_dict), 1)

        self.assertEqual(msg_dict[0]["user_id"], self.user1.id)
        self.assertEqual(msg_dict[0]["url"], self.project1.get_absolute_url())
        self.assertEqual(msg_dict[0]["prj_cd"], self.project1.prj_cd)
        self.assertEqual(msg_dict[0]["prj_nm"], self.project1.prj_nm)
        self.assertEqual(msg_dict[0]["msg_id"], messages[0].id)

        # approve the project to create a new message
        self.project1.approve()

        # we should have two messages now
        messages = my_messages(self.user1)
        msg_dict = get_messages_dict(messages)
        self.assertEqual(len(msg_dict), 2)

        self.assertEqual(msg_dict[0]["user_id"], self.user1.id)
        self.assertEqual(msg_dict[0]["url"], self.project1.get_absolute_url())
        self.assertEqual(msg_dict[0]["prj_cd"], self.project1.prj_cd)
        self.assertEqual(msg_dict[0]["prj_nm"], self.project1.prj_nm)
        self.assertEqual(msg_dict[0]["msg_id"], messages[0].id)
        # verify that the msg_id is correct
        self.assertEqual(msg_dict[1]["msg_id"], messages[1].id)

    def test_messages_dict_discontiguous_messages(self):
        """this test is exactly the same as test_message_dict except that
        george is sent a bunch of fake messages between jerry's
        sumbitted and approved messaages.  Jerry should get the same 2
        messages back regardless of how many other messages have been
        sent to other users.

        """

        # get the messages for our user
        messages = my_messages(self.user1)
        # get the dictionary which include project, user and message info
        msg_dict = get_messages_dict(messages)
        self.assertEqual(len(msg_dict), 1)

        self.assertEqual(msg_dict[0]["user_id"], self.user1.id)
        self.assertEqual(msg_dict[0]["url"], self.project1.get_absolute_url())
        self.assertEqual(msg_dict[0]["prj_cd"], self.project1.prj_cd)
        self.assertEqual(msg_dict[0]["prj_nm"], self.project1.prj_nm)
        self.assertEqual(msg_dict[0]["msg_id"], messages[0].id)

        # send george a bunch of fake messages
        for msg in range(15):
            msgtxt = "a fake message - {0}.".format(msg)
            send_message(
                msgtxt=msgtxt,
                recipients=self.user2,
                project=self.project2,
                milestone=self.milestone3,
            )
        messages = my_messages(self.user2)
        # verify that george got the fake messages (+1 for his project)
        self.assertEqual(messages.count(), 15 + 1)

        # approve the project to create a new message
        self.project1.approve()

        # we should have two messages now
        messages = my_messages(self.user1)
        msg_dict = get_messages_dict(messages)
        self.assertEqual(len(msg_dict), 2)

        self.assertEqual(msg_dict[0]["user_id"], self.user1.id)
        self.assertEqual(msg_dict[0]["url"], self.project1.get_absolute_url())
        self.assertEqual(msg_dict[0]["prj_cd"], self.project1.prj_cd)
        self.assertEqual(msg_dict[0]["prj_nm"], self.project1.prj_nm)
        self.assertEqual(msg_dict[0]["msg_id"], messages[0].id)
        # verify that the msg_id is correct
        self.assertEqual(msg_dict[1]["msg_id"], messages[1].id)


# ==================================


class TestSendMessages(TestCase):
    """Some simple tests to verify that the functions associated with the
    messaging system function as expected.  send_messages should be able
    to send a simple message to a number of recipients.
    """

    def setUp(self):
        """Set up a fairly complicated employee heirachy with 6 employees"""

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        self.user3 = UserFactory(
            first_name="Cosmo", last_name="Kramer", username="ckramer"
        )
        self.user4 = UserFactory(
            first_name="Elaine", last_name="Benis", username="ebenis"
        )

        # now setup employee relationships
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        # George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2, supervisor=self.employee1)
        # Kramer works for Jerry
        self.employee3 = EmployeeFactory(user=self.user3, supervisor=self.employee1)
        # Elaine works for Kramer
        self.employee4 = EmployeeFactory(user=self.user4, supervisor=self.employee3)

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Approved", category="Core", order=1, report=False
        )

        # now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(
            prj_cd="LHA_IA12_111", prj_ldr=self.user3, owner=self.user3, dba=self.user2
        )

    def test_send_messages(self):
        """Verify that we can send a simple message to several people."""

        # make sure the tables are empty
        messages = Message.objects.all().count()
        self.assertEqual(messages, 0)

        messages2users = Messages2Users.objects.all().count()
        self.assertEqual(messages, 0)

        # build the list of recipients
        send_to = [self.user1, self.user2, self.user3]
        msgtxt = "a fake message."

        send_message(
            msgtxt=msgtxt,
            recipients=send_to,
            project=self.project1,
            milestone=self.milestone1,
        )

        # verify that the message is in the message table
        messages = Message.objects.all()
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages[0].msgtxt, msgtxt)

        # verify that there is a record in message2user for each recipient
        messages2users = Messages2Users.objects.all()
        self.assertEqual(messages2users.count(), 3)

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


class TestMyMessages(TestCase):
    """The helper function my_messages accepts a user and returns all of
    the Messages2Users objects associated with that user. my_messages()
    should be able to retrieve both read and unread messages for a
    particular user.
    """

    def setUp(self):
        """we will need two users, a project, a project milestone, and four
        messages.

        """

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        # now setup employee relationships
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        # George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2, supervisor=self.employee1)

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Submitted", category="Core", order=1, report=False
        )

        # now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(
            prj_cd="LHA_IA12_111", prj_ldr=self.user1, owner=self.user1, dba=self.user1
        )

        pms = self.project1.get_milestones()[0]

        self.msgtxt = [
            "the first message.",
            "the second message.",
            "the third message.",
            "the fourth message.",
        ]

        now = datetime.datetime.now(pytz.utc)
        # now = datetime.datetime.utcnow()
        read = [now, now, None, None]

        # create 4 messages and 4 message2user objects - two of the
        # message2user objects will have a time stamp.
        for txt, ts in zip(self.msgtxt, read):
            message = Message(msgtxt=txt, project_milestone=pms)
            message.save()
            msg4u = Messages2Users(user=self.user1, message=message, read=ts)
            msg4u.save()

        # we need to update the created field for each of the
        # message2user objects. Right now, they are too close together
        # to reliably sort correctly (their timestamps are all the same)
        created = []
        yesterday = now - datetime.timedelta(days=1)
        for x in range(4):
            created.append(yesterday + datetime.timedelta(minutes=x))

        msgs = Messages2Users.objects.all()
        for msg, ts in zip(msgs, created):
            msg.created = ts
            msg.save()

    def test_my_messages_only_unread(self):
        """by default, my_messages should only include those messages that
        have not been read yet (i.e. [read] is null)"""

        msgs = my_messages(self.user1)
        # self.assertCountEqual(msgs, self.msgtxt[2:])
        should_be = self.msgtxt[2:]
        should_be.reverse()
        should_be.extend(["Submitted"])

        self.assertQuerysetEqual(
            msgs, should_be, lambda a: str(a.message.msgtxt), ordered=False
        )

    def test_my_messages_all(self):
        """We may want to see all of the messages that have been sent to a
        user, verify that we get them (order does not matter)."""

        msgs = my_messages(self.user1, all=True)

        should_be = self.msgtxt
        should_be.reverse()
        should_be.extend(["Submitted"])

        self.assertQuerysetEqual(
            msgs, should_be, lambda a: str(a.message.msgtxt), ordered=False
        )

    def test_my_messages_no_messages(self):
        """If there aren't any messages for this user, return an empty list
        (gracefully)"""

        msgs = my_messages(self.user2)
        self.assertCountEqual(msgs, [])

    def tearDown(self):
        self.project1.delete()
        self.milestone1.delete()

        self.employee1.delete()
        self.employee2.delete()

        self.user1.delete()
        self.user2.delete()


class TestSendNoticeWhenProjectMilestonesChange(TestCase):
    """Verify that when project milestones are updated, messages are sent
    to the project lead, their supervisor and the dba."""

    def setUp(self):
        """for these tests, we need a project, some milestones, a project
        lead, a supervisor and a dba"""

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        self.user3 = UserFactory(
            first_name="Cosmo", last_name="Kramer", username="ckramer"
        )

        # now setup employee relationships
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        # George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2, supervisor=self.employee1)
        # Kramer works for Jerry
        self.employee3 = EmployeeFactory(user=self.user3, supervisor=self.employee1)

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Submitted", category="Core", order=1, report=False
        )

        self.milestone2 = MilestoneFactory.create(
            label="Approved", category="Core", order=2, report=False
        )

        MilestoneFactory(label="Sign Off")

        # now create a project with an owner and dba.
        self.project1 = ProjectFactory.create(
            prj_cd="LHA_IA12_111", owner=self.user3, dba=self.user2
        )

    def test_send_message_project_approved(self):
        """When Jerry approves the project, Jerry, George and Kramer should
        all get a message stating that it has been approved."""

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

        for msg in Georges_msgs:
            print("msg = %s" % msg)

        self.assertEqual(Georges_msgs.count(), 2)
        self.assertEqual(Jerrys_msgs.count(), 2)
        self.assertEqual(Kramers_msgs.count(), 2)

        # check on of the users to verify that they message they
        # recieve is what you think it should be:
        self.assertEqual(Georges_msgs[0].message.msgtxt, "Approved")
        self.assertEqual(Georges_msgs[1].message.msgtxt, "Submitted")

    def test_send_message_project_unapproved(self):
        """If a project is approved and subsquently un-approved, the project
        lead should get a meaningful message for each event."""

        # approve the project
        self.project1.approve()
        # immediately unapprove it
        self.project1.unapprove()

        Georges_msgs = my_messages(self.user2)

        for msg in Georges_msgs:
            print(msg.message)

        self.assertEqual(Georges_msgs.count(), 3)

        # check on of the users to verify that they message they
        # recieve is what you think it should be:
        msgtxt = "The milestone 'Approved' has been revoked"
        self.assertEqual(Georges_msgs[0].message.msgtxt, msgtxt)
        self.assertEqual(Georges_msgs[1].message.msgtxt, "Approved")
        self.assertEqual(Georges_msgs[2].message.msgtxt, "Submitted")

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


class TestSumbittedMessage(TestCase):
    """When a project is created, a post-save signal hook should send a
    submitted message to the submitted employee and their boss.
    """

    def setUp(self):
        """for these tests, we need a project, some milestones, a project
        lead, a supervisor and a dba"""

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        # There are no employee relationships.
        # george has no boss
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        self.employee2 = EmployeeFactory(user=self.user2, supervisor=self.employee1)

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Submitted", category="Core", order=1, report=False
        )

        self.milestone2 = MilestoneFactory.create(
            label="Approved", category="Core", order=2, report=False
        )

    def test_submitted_message(self):
        """This test verifies that the 'sumbitted' message is sent
        automatically when a project is created.  Unlike other
        notices, submitted uses a post save hook.

        """

        # verify that there aren't any messages when we start
        Jerrys_msgs = my_messages(self.user1)
        Georges_msgs = my_messages(self.user2)

        self.assertEqual(0, len(Jerrys_msgs))
        self.assertEqual(0, len(Georges_msgs))

        # now create a project owned by george
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111", owner=self.user2)

        # verify that both george and his boss get a notice and that it
        # contains the word 'submitted'
        Jerrys_msgs = my_messages(self.user1)
        Georges_msgs = my_messages(self.user2)

        self.assertEqual(1, len(Jerrys_msgs))
        self.assertIn("Submitted", Jerrys_msgs[0].message.msgtxt)

        self.assertEqual(1, len(Georges_msgs))
        self.assertIn("Submitted", Jerrys_msgs[0].message.msgtxt)
