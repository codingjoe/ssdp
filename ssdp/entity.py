import email.parser
import logging

__all__ = ("SSDPMessage", "SSDPRequest", "SSDPResponse")


logger = logging.getLogger("ssdp.entity")


class SSDPMessage:
    """Simplified HTTP message to serve as a SSDP message."""

    def __init__(self, version="HTTP/1.1", headers=None):
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
        if msg.startswith("HTTP/"):
            return SSDPResponse.parse(msg)
        else:
            return SSDPRequest.parse(msg)

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
        return self.__str__().encode().replace(b"\n", b"\r\n")


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
        headers = cls.parse_headers("\r\n".join(lines[1:]))
        return cls(
            version=version, status_code=status_code, reason=reason, headers=headers
        )

    def __str__(self):
        """Return complete SSDP response."""
        lines = list()
        lines.append(" ".join([self.version, str(self.status_code), self.reason]))
        for header in self.headers:
            lines.append("%s: %s" % header)
        return "\n".join(lines)


class SSDPRequest(SSDPMessage):
    """Simple Service Discovery Protocol (SSDP) request."""

    def __init__(self, method, uri="*", version="HTTP/1.1", headers=None):
        self.method = method
        self.uri = uri
        super().__init__(version=version, headers=headers)

    @classmethod
    def parse(cls, msg):
        """Parse message string to request object."""
        lines = msg.splitlines()
        method, uri, version = lines[0].split()
        headers = cls.parse_headers("\r\n".join(lines[1:]))
        return cls(version=version, uri=uri, method=method, headers=headers)

    def sendto(self, transport, addr):
        """
        Send request to a given address via given transport.

        Args:
            transport
                Write transport to send the message on.
            addr (Tuple[str, int]):
                IP address and port pair to send the message to.

        """
        msg = bytes(self) + b"\r\n"
        logger.debug("%s:%s < %s", *(addr + (self,)))
        transport.sendto(msg, addr)

    def __str__(self):
        """Return complete SSDP request."""
        lines = list()
        lines.append(" ".join([self.method, self.uri, self.version]))
        for header in self.headers:
            lines.append("%s: %s" % header)
        return "\n".join(lines)
