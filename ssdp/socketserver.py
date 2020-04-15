import logging
import socket
import socketserver
from ssdp.entity import *
from ssdp.network import *
import struct
import typing


logger = logging.getLogger('ssdp.socketserver')


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        packet_bytes = self.request[0]
        try:
            packet_str = packet_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return

        msg = SSDPMessage.parse(packet_str)
        if isinstance(msg, SSDPRequest):
            logger.debug("request received: %s from %s", str(msg), self.request[1])
            self.request_received(msg)
        elif isinstance(msg, SSDPResponse):
            logger.debug("response received: %s from %s", str(msg), self.request[1])
            self.response_received(msg)
        else:
            logger.debug("unknown received: %s from %s", str(msg), self.request[1])

    def request_received(self, request: SSDPRequest):
        raise NotImplementedError()

    def resonse_received(self, response: SSDPResponse):
        raise NotImplementedError()


class Server6(socketserver.UDPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True

    def server_bind(self):
        s = self.socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.server_address)
        try:
            s.setsockopt(socket.IPPROTO_IPV6, 20,  # IPV6_ADD_MEMBERSHIP
                struct.pack("16si", socket.inet_pton(socket.AF_INET6, self.server_address[0]), self.server_address[3])  # struct ipv6_mreq
            )
        except OSError as err:
            logging.error('Failed to subscribe to IPv6 multicast. Error: %d, %s' % (err.errno, err.strerror))

    def __init__(self, ifindex: int, request_handler: typing.Callable[[], RequestHandler]):
        self.ifindex = ifindex
        super(Server6, self).__init__((str(MULTICAST_ADDRESS_IPV6_LINK_LOCAL), PORT, 0, ifindex), request_handler)

