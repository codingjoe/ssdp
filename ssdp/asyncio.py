import asyncio
import errno
import logging

from . import messages

logger = logging.getLogger(__name__)


class SimpleServiceDiscoveryProtocol(asyncio.DatagramProtocol):
    """
    Simple Service Discovery Protocol (SSDP).

    SSDP is part of UPnP protocol stack. For more information see:
    https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol
    """

    def datagram_received(self, data, addr):
        data = data.decode()
        logger.debug("%s:%s – – %s", *addr, data)

        if data.startswith("HTTP/"):
            self.process_response(messages.SSDPResponse.parse(data), addr)
        else:
            self.process_request(messages.SSDPRequest.parse(data), addr)

    def process_response(self, response, addr):
        """
        Being called when some response is received.

        Args:
            response (ssdp.messages.SSDPResponse): Received response.
            addr (Tuple[str, int]): Tuple containing IP address and port number.

        """
        raise NotImplementedError()

    def process_request(self, request, addr):
        """
        Being called when some request is received.

        Args:
            request (ssdp.messages.SSDPRequest): Received request.
            addr (Tuple[str, int]): Tuple containing IP address and port number.

        """
        raise NotImplementedError()

    def error_received(self, exc):
        if exc == errno.EAGAIN or exc == errno.EWOULDBLOCK:
            logger.exception("Blocking IO error", exc_info=exc)
        else:
            raise exc

    def connection_lost(self, exc):
        logger.exception("Connection lost", exc_info=exc)
