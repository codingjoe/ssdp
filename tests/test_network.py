import socket
import sys

import pytest
from ssdp import network


def test_get_best_family():
    assert network.get_best_family("::", 1900) == (
        socket.AF_INET6,
        ("::", 1900, 0, 0),
    )


@pytest.mark.skipif(sys.platform != "win32", reason="tests for windows only")
def test_get_best_family__win32():
    assert network.get_best_family(None, 1900) == (
        socket.AF_INET,
        ("0.0.0.0", 1900, 0, 0),  # noqa S104
    )
