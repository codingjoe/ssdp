"""Python library for Simple Service Discovery Protocol (SSDP)."""

import ssdp.entity as entity
import ssdp.network as network
import ssdp.asyncio as asyncio

from .entity import *
from .asyncio import *
from . import _version

__all__ = entity.__all__ + asyncio.__all__


__version__ = _version.version
VERSION = _version.version_tuple
