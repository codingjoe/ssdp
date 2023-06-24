"""Python asyncio library for Simple Service Discovery Protocol (SSDP)."""

from . import _version
from .aio import SimpleServiceDiscoveryProtocol
from .deprecation import moved
from .messages import SSDPMessage, SSDPRequest, SSDPResponse

__version__ = _version.version
__all__ = []

VERSION = _version.version_tuple

SimpleServiceDiscoveryProtocol = moved(SimpleServiceDiscoveryProtocol)
SSDPMessage = moved(SSDPMessage)
SSDPRequest = moved(SSDPRequest)
SSDPResponse = moved(SSDPResponse)
