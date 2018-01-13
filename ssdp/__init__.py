"""Python asyncio library for Simple Service Discovery Protocol (SSDP)."""
import asyncio
import email.parser
import errno
import logging

__all__ = ('SSDPRequest', 'SSDPResponse', 'SimpleServiceDiscoveryProtocol')

logger = logging.getLogger('ssdp')


class SSDPMessage:
    """Simplified HTTP message to serve as a SSDP message."""

    def __init__(self, version='HTTP/1.1', headers=None):
        if headers is None:
            headers = []
        elif isinstance(headers, dict):
            headers = headers.items()

        self.version = version
        self.headers = list(headers)

    @classmethod
    def parse(cls, msg):
        """
        Parse message from string.

        Args:
            msg (str): Message string.

        Returns:
            SSDPMessage: Message parsed from string.

        """
        raise NotImplementedError()

    @classmethod
    def parse_headers(cls, msg):
        """
        Parse HTTP headers.

        Args:
            msg (str): HTTP message.

        Returns:
            (List[Tuple[str, str]): List of header tuples.

        """
        return list(email.parser.Parser().parsestr(msg).items())

    def __str__(self):
        """Return complete HTTP message."""
        raise NotImplementedError()

    def __bytes__(self):
        """Return complete HTTP message as bytes."""
        return self.__str__().encode().replace(b'\n', b'\r\n')


class SSDPResponse(SSDPMessage):
    """Simple Service Discovery Protocol (SSDP) response."""

    def __init__(self, status_code, reason, **kwargs):
        self.status_code = int(status_code)
        self.reason = reason
        super().__init__(**kwargs)

    @classmethod
    def parse(cls, msg):
        """Parse message string to response object."""
        lines = msg.splitlines()
        version, status_code, reason = lines[0].split()
        headers = cls.parse_headers('\r\n'.join(lines[1:]))
        return cls(version=version, status_code=status_code,
                   reason=reason, headers=headers)

    def __str__(self):
        """Return complete SSDP response."""
        lines = list()
        lines.append(' '.join(
            [self.version, str(self.status_code), self.reason]
        ))
        for header in self.headers:
            lines.append('%s: %s' % header)
        return '\n'.join(lines)


class SSDPRequest(SSDPMessage):
    """Simple Service Discovery Protocol (SSDP) request."""

    def __init__(self, method, uri='*', version='HTTP/1.1', headers=None):
        self.method = method
        self.uri = uri
        super().__init__(version=version, headers=headers)

    @classmethod
    def parse(cls, msg):
        """Parse message string to request object."""
        lines = msg.splitlines()
        method, uri, version = lines[0].split()
        headers = cls.parse_headers('\r\n'.join(lines[1:]))
        return cls(version=version, uri=uri, method=method, headers=headers)

    def sendto(self, transport, addr):
        """
        Send request to a given address via given transport.

        Args:
            transport (asyncio.DatagramTransport):
                Write transport to send the message on.
            addr (Tuple[str, int]):
                IP address and port pair to send the message to.

        """
        msg = bytes(self) + b'\r\n'
        logger.debug("%s:%s < %s", *(addr + (self,)))
        transport.sendto(msg, addr)

    def __str__(self):
        """Return complete SSDP request."""
        lines = list()
        lines.append(' '.join(
            [self.method, self.uri, self.version]
        ))
        for header in self.headers:
            lines.append('%s: %s' % header)
        return '\n'.join(lines)


class SimpleServiceDiscoveryProtocol(asyncio.DatagramProtocol):
    """
    Simple Service Discovery Protocol (SSDP).

    SSDP is part of UPnP protocol stack. For more information see:
    https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol
    """

    MULTICAST_ADDRESS = '239.255.255.250'

    def datagram_received(self, data, addr):
        data = data.decode()
        logger.debug("%s:%s > %s", *(addr + (data,)))

        if data.startswith('HTTP/'):
            self.response_received(SSDPResponse.parse(data), addr)
        else:
            self.request_received(SSDPRequest.parse(data), addr)

    def response_received(self, response, addr):
        """
        Called when some response is received.

        Args:
            response (SSDPResponse): Received response.
            addr (Tuple[str, int]: Tuple containing IP address and port number.

        """
        raise NotImplementedError()

    def request_received(self, request, addr):
        """
        Called when some request is received.

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
