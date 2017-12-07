import pytest

from pjtk2.functions import strip_carriage_returns



def test_strip_carriage_returns():
    """
    """

    A = "pink salmon\r\nchum salmon\r\ncoho salmon\r\nsockeye salmon"

    A_shouldbe = "pink salmon chum salmon coho salmon sockeye salmon"
    assert strip_carriage_returns(A) == A_shouldbe

    B = ("pink salmon\r\n\r\nchum salmon\r\ncoho salmon\r\n\r\nsockeye " +
    "salmon\r\nchinook salmon")

    B_shouldbe = ("pink salmon \r\n\r\nchum salmon coho salmon \r\n\r\n" +
    "sockeye salmon chinook salmon")

    assert strip_carriage_returns(B) == B_shouldbe


def test_strip_carriage_returns_None():
    """If we pass in None, it should return None,
    """

    assert strip_carriage_returns(None) is None
