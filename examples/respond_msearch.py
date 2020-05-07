#!/usr/bin/env python3
"""Waiting for a M-SEARCH request and respond to it."""
import asyncio
import socket

import ssdp


class MyProtocol(ssdp.SimpleServiceDiscoveryProtocol):
    """Protocol to handle responses and requests."""

    def response_received(self, response: ssdp.SSDPResponse, addr: tuple):
        """Handle an incoming response."""
        print(
            "received response: {} {} {}".format(
                response.status_code, response.reason, response.version
            )
        )

        for header in response.headers:
            print("header: {}".format(header))

        print()

    def request_received(self, request: ssdp.SSDPRequest, addr: tuple):
        """Handle an incoming request and respond to it."""
        print(
            "received request: {} {} {}".format(
                request.method, request.uri, request.version
            )
        )

        for header in request.headers:
            print("header: {}".format(header))

        print()

        # Build response and send it.
        print("Sending a response back to {}:{}".format(*addr))
        ssdp_response = ssdp.SSDPResponse(
            200,
            "OK",
            headers={
                "Cache-Control": "max-age=30",
                "Location": "http://127.0.0.1:80/Device.xml",
                "Server": "Python UPnP/1.0 SSDP",
                "ST": "urn:schemas-upnp-org:service:ExampleService:1",
                "USN": "uuid:2fac1234-31f8-11b4-a222-08002b34c003::urn:schemas-upnp-org:service:Example:1",
                "EXT": "",
            },
        )
        ssdp_response.sendto(self.transport, addr)


def main():
    # Start the asyncio loop.
    loop = asyncio.get_event_loop()
    connect = loop.create_datagram_endpoint(
        MyProtocol,
        family=socket.AF_INET,
        local_addr=(MyProtocol.MULTICAST_ADDRESS, 1900),
    )
    transport, protocol = loop.run_until_complete(connect)

    # Ensure MyProtocol has something send to.
    MyProtocol.transport = transport

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()


if __name__ == "__main__":
    main()
