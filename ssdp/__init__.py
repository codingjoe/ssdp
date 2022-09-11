"""Python library for Simple Service Discovery Protocol (SSDP)."""

from . import _version
from .asyncio import *  # noqa
from .entity import *  # noqa
from .network import *  # noqa
from .socketserver import *  # noqa

__version__ = _version.version
VERSION = _version.version_tuple
