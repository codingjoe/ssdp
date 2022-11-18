#!/usr/bin/env python3
"""Send out a M-SEARCH request and listening for responses."""
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
        """Handle an incoming request."""
        print(
            "received request: {} {} {}".format(
                request.method, request.uri, request.version
            )
        )

        for header in request.headers:
            print("header: {}".format(header))

        print()


async def main():
    # Start the asyncio loop.
    loop = asyncio.get_event_loop()
    connect = loop.create_datagram_endpoint(MyProtocol, family=socket.AF_INET)
    transport, protocol = await connect

    # Send out an M-SEARCH request, requesting all service types.
    search_request = ssdp.SSDPRequest(
        "M-SEARCH",
        headers={
            "HOST": "239.255.255.250:1900",
            "MAN": '"ssdp:discover"',
            "MX": "4",
            "ST": "ssdp:all",
        },
    )
    search_request.sendto(transport, (MyProtocol.MULTICAST_ADDRESS, 1900))

    # Keep on running for 4 seconds.
    try:
        await asyncio.sleep(4)
    except KeyboardInterrupt:
        pass

    transport.close()


if __name__ == "__main__":
    asyncio.run(main())
