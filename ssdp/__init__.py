"""Python library for Simple Service Discovery Protocol (SSDP)."""

import ssdp.asyncio as asyncio
import ssdp.entity as entity
import ssdp.network as network
from ssdp.asyncio import *
from ssdp.entity import *

__all__ = entity.__all__ + asyncio.__all__
