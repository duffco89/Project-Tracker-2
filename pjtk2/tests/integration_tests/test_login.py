import pytest

from pjtk2.tests.pytest_fixtures import user

def test_with_authenticated_client(client, user):

#    pwd = "Abcd1234"
#    user.set_password(pwd)
#    user.save()
    login = client.login(username=user.username,
                         password='Abcd1234')
    assert login is True
