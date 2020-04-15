import ipaddress


MULTICAST_ADDRESS_IPV4 = ipaddress.IPv4Address('239.255.255.250')
MULTICAST_ADDRESS_IPV6_LINK_LOCAL = ipaddress.IPv6Address('ff02::c')
MULTICAST_ADDRESS_IPV6_SITE_LOCAL = ipaddress.IPv6Address('ff05::c')
MULTICAST_ADDRESS_IPV6_ORG_LOCAL = ipaddress.IPv6Address('ff08::c')
MULTICAST_ADDRESS_IPV6_GLOBAL = ipaddress.IPv6Address('ff0e::c')

PORT = 1900
