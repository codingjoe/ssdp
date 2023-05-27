import logging
import socket
import socketserver
import struct

from . import messages, network

logger = logging.getLogger(__name__)


class SSDPMessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        data = data.decode()
        logger.debug("%s:%d – – %s", *self.client_address, data)

        if data.startswith("HTTP/"):
            self.process_response(
                messages.SSDPResponse.parse(data), self.client_address
            )
        else:
            self.process_request(messages.SSDPRequest.parse(data), self.client_address)

    def process_request(
        self, request: messages.SSDPRequest, client_address: tuple[str, int]
    ):
        raise NotImplementedError()

    def process_response(
        self, response: messages.SSDPResponse, client_address: tuple[str, int]
    ):
        raise NotImplementedError()


class SSDPServer(socketserver.UDPServer):
    allow_reuse_address = True

    def server_bind(self):
        if self.address_family == socket.AF_INET:
            self.socket.setsockopt(
                socket.IPPROTO_IP,
                socket.IP_ADD_MEMBERSHIP,
                socket.inet_aton(network.MULTICAST_ADDRESS_IPV4) + struct.pack("@I", 0),
            )
        elif self.address_family == socket.AF_INET6:
            ifis = struct.pack("@I", 0)
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF, ifis)
            group = (
                socket.inet_pton(
                    self.address_family, network.MULTICAST_ADDRESS_IPV6_SITE_LOCAL
                )
                + ifis
            )
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, group)
        self.socket.bind(self.server_address[:2])
