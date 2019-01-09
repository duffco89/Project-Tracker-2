'''
test for the files in pjtk2.functions.
'''


from pjtk2.functions import make_possessive


def test_make_posssive():
    '''
    Make possessive should return the string plus a "'s" if it ends
    with anything but and s.  If it ends in an "s", it should just
    append an apostrophe.

    '''
    assert make_possessive('Bob') == "Bob's"
    assert make_possessive('Chris') == "Chris'"
