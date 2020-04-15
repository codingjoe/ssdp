"""Python library for Simple Service Discovery Protocol (SSDP)."""

import ssdp.asyncio as asyncio
import ssdp.entity as entity
import ssdp.network as network

from .asyncio import *
from .entity import *
from . import _version

__all__ = entity.__all__ + asyncio.__all__


__version__ = _version.version
VERSION = _version.version_tuple
