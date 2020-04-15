import asyncio
import errno
import logging
from ssdp.entity import *


__all__ = ['SimpleServiceDiscoveryProtocol']

logger = logging.getLogger('ssdp.asyncio')


class SimpleServiceDiscoveryProtocol(asyncio.DatagramProtocol):
    """
    Simple Service Discovery Protocol (SSDP).

    SSDP is part of UPnP protocol stack. For more information see:
    https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol
    """

    def datagram_received(self, data, addr):
        data = data.decode()
        logger.debug("%s:%s > %s", *(addr + (data,)))

        msg = SSDPMessage.parse(data)
        if isinstance(msg, SSDPResponse):
            self.response_received(msg, addr)
        elif isinstance(msg, SSDPRequest):
            self.request_received(msg, addr)
        else:
            pass

    def response_received(self, response, addr):
        """
        Call when some response is received.

        Args:
            response (SSDPResponse): Received response.
            addr (Tuple[str, int]: Tuple containing IP address and port number.

        """
        raise NotImplementedError()

    def request_received(self, request, addr):
        """
        Call when some request is received.

        Args:
            request (SSDPRequest): Received request.
            addr (Tuple[str, int]: Tuple containing IP address and port number.

        """
        raise NotImplementedError()

    def error_received(self, exc):
        if exc == errno.EAGAIN or exc == errno.EWOULDBLOCK:
            logger.error('Error received: %s', exc)
        else:
            raise IOError("Unexpected connection error") from exc

    def connection_lost(self, exc):
        logger.exception("Socket closed, stop the event loop", exc_info=exc)
        loop = asyncio.get_event_loop()
        loop.stop()
