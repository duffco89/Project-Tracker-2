import pytest

from ..utils.helpers import strip_carriage_returns, make_possessive


def test_strip_carriage_returns():
    """
    """

    A = "pink salmon\r\nchum salmon\r\ncoho salmon\r\nsockeye salmon"

    A_shouldbe = "pink salmon chum salmon coho salmon sockeye salmon"
    assert strip_carriage_returns(A) == A_shouldbe

    B = (
        "pink salmon\r\n\r\nchum salmon\r\ncoho salmon\r\n\r\nsockeye "
        + "salmon\r\nchinook salmon"
    )

    B_shouldbe = (
        "pink salmon \r\n\r\nchum salmon coho salmon \r\n\r\n"
        + "sockeye salmon chinook salmon"
    )

    assert strip_carriage_returns(B) == B_shouldbe


def test_strip_carriage_returns_None():
    """If we pass in None, it should return None,
    """

    assert strip_carriage_returns(None) is None


def test_make_posssive():
    """
    Make possessive should return the string plus a "'s" if it ends
    with anything but and s.  If it ends in an "s", it should just
    append an apostrophe.

    """
    assert make_possessive("Bob") == "Bob's"
    assert make_possessive("Chris") == "Chris'"
