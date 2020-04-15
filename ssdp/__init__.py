"""Python asyncio library for Simple Service Discovery Protocol (SSDP)."""
import abc
import asyncio
import email.parser
import errno
import logging

__all__ = ("SSDPRequest", "SSDPResponse", "SimpleServiceDiscoveryProtocol")

from typing import Iterable, Tuple, List

logger = logging.getLogger("ssdp")


class SSDPMessage(abc.ABC):
    """Simplified HTTP message to serve as a SSDP message."""

    def __init__(
        self, version: str = "HTTP/1.1", headers: Iterable[Tuple[str, str]] = None
    ):
        if headers is None:
            headers = []
        elif isinstance(headers, dict):
            headers = headers.items()

        self.version = version
        self.headers = list(headers)

    @classmethod
    @abc.abstractmethod
    def parse(cls, msg: str) -> "SSDPMessage":
        """
        Parse message from a string into a :class:`SSDPMessage` instance.

        Args:
            msg (str): Message string.

        Returns:
            SSDPMessage: Message parsed from string.

        """

    @classmethod
    def parse_headers(cls, msg: str) -> List[Tuple[str, str]]:
        """
        Parse HTTP headers to list.

        Args:
            msg (str): HTTP message.

        Returns:
            (List[Tuple[str, str]]): List of header tuples.

        """
        return list(email.parser.Parser().parsestr(msg).items())

    @abc.abstractmethod
    def __str__(self) -> str:
        """Return complete HTTP message."""

    def __bytes__(self) -> bytes:
        """Return complete HTTP message as bytes."""
        return self.__str__().encode().replace(b"\n", b"\r\n")


class SSDPResponse(SSDPMessage):
    """Simple Service Discovery Protocol (SSDP) response."""

    def __init__(self, status_code: [int, float, str], reason: str, **kwargs):
        self.status_code: int = int(status_code)
        self.reason: str = reason
        super().__init__(**kwargs)

    @classmethod
    def parse(cls, msg: str) -> "SSDPResponse":
        """Parse message string to response object."""
        lines = msg.splitlines()
        version, status_code, reason = lines[0].split()
        headers = cls.parse_headers("\r\n".join(lines[1:]))
        return cls(
            version=version, status_code=status_code, reason=reason, headers=headers
        )

    def __str__(self) -> str:
        """Return complete SSDP response."""
        lines = list()
        lines.append(" ".join([self.version, str(self.status_code), self.reason]))
        for header in self.headers:
            lines.append("%s: %s" % header)
        return "\n".join(lines)


class SSDPRequest(SSDPMessage):
    """Simple Service Discovery Protocol (SSDP) request."""

    def __init__(
        self,
        method: str,
        uri: str = "*",
        version: str = "HTTP/1.1",
        headers: Iterable[Tuple[str, str]] = None,
    ):
        self.method: str = method
        self.uri = uri
        super().__init__(version=version, headers=headers)

    @classmethod
    def parse(cls, msg) -> "SSDPRequest":
        """Parse message string to request object."""
        lines = msg.splitlines()
        method, uri, version = lines[0].split()
        headers = cls.parse_headers("\r\n".join(lines[1:]))
        return cls(version=version, uri=uri, method=method, headers=headers)

    def sendto(self, transport: asyncio.DatagramTransport, addr: Tuple[str, int]):
        """
        Send request to a given address via given transport.

        Args:
            transport (asyncio.DatagramTransport):
                Write transport to send the message on.
            addr (Tuple[str, int]):
                IP address and port pair to send the message to.

        """
        msg = bytes(self) + b"\r\n"
        logger.debug("%s:%s < %s", *(addr + (self,)))
        transport.sendto(msg, addr)

    def __str__(self):
        """Return full SSDP request."""
        lines = list()
        lines.append(" ".join([self.method, self.uri, self.version]))
        for header in self.headers:
            lines.append("%s: %s" % header)
        return "\n".join(lines)


class SimpleServiceDiscoveryProtocol(asyncio.DatagramProtocol, abc.ABC):
    """
    Simple Service Discovery Protocol (SSDP).

    SSDP is part of UPnP protocol stack. For more information see:
    https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol
    """

    MULTICAST_ADDRESS = "239.255.255.250"

    def datagram_received(self, data, addr):
        data = data.decode()
        logger.debug("%s:%s > %s", *(addr + (data,)))

        if data.startswith("HTTP/"):
            self.response_received(SSDPResponse.parse(data), addr)
        else:
            self.request_received(SSDPRequest.parse(data), addr)

    @abc.abstractmethod
    def response_received(self, response: SSDPResponse, addr: Tuple[str, int]):
        """
        Being called when some response is received.

        Args:
            response (SSDPResponse): Received response.
            addr (Tuple[str, int]): Tuple containing IP address and port number.

        """

    @abc.abstractmethod
    def request_received(self, request: SSDPRequest, addr: Tuple[str, int]):
        """
        Being called when some request is received.

        Args:
            request (SSDPRequest): Received request.
            addr (Tuple[str, int]): Tuple containing IP address and port number.

        """

    def error_received(self, exc):
        if exc == errno.EAGAIN or exc == errno.EWOULDBLOCK:
            logger.error("Error received: %s", exc)
        else:
            raise IOError("Unexpected connection error") from exc

    def connection_lost(self, exc):
        logger.exception("Socket closed, stop the event loop", exc_info=exc)
        loop = asyncio.get_event_loop()
        loop.stop()
