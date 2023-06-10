import pytest

from ssdp import deprecation


def _fn():
    pass


def test_moved():
    with pytest.deprecated_call() as warning:
        deprecation.moved(_fn)()

    assert (
        str(warning.list[0].message)
        == "'ssdp.deprecation._fn' has moved. Please import from: tests.test_deprecation._fn"
    )
