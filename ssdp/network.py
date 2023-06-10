import socket
import sys

__all__ = [
    "MULTICAST_ADDRESS_IPV4",
    "MULTICAST_ADDRESS_IPV6_LINK_LOCAL",
    "MULTICAST_ADDRESS_IPV6_SITE_LOCAL",
    "MULTICAST_ADDRESS_IPV6_ORG_LOCAL",
    "MULTICAST_ADDRESS_IPV6_GLOBAL",
    "PORT",
]


MULTICAST_ADDRESS_IPV4 = "239.255.255.250"
MULTICAST_ADDRESS_IPV6_LINK_LOCAL = "ff02::c"
MULTICAST_ADDRESS_IPV6_SITE_LOCAL = "ff05::c"
MULTICAST_ADDRESS_IPV6_ORG_LOCAL = "ff08::c"
MULTICAST_ADDRESS_IPV6_GLOBAL = "ff0e::c"

PORT = 1900


def get_best_family(*address):
    """Backport of private `http.server._get_best_family`."""
    family = socket.AF_INET if sys.platform == "win32" else 0

    infos = socket.getaddrinfo(
        *address,
        family=family,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, type, proto, canonname, sockaddr = next(iter(infos))
    return family, sockaddr
