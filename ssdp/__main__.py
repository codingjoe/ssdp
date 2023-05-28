#!/usr/bin/env python3
import asyncio
import logging
import platform
import socket
import sys
import time
from http.server import _get_best_family

import ssdp.asyncio
import ssdp.messages
from ssdp import network
from ssdp.server import SSDPMessageHandler, SSDPServer

try:
    import click

    from .lexers import prettify_msg
except ImportError:
    print("The SSDP CLI requires needs to be installed via `pip install ssdp[cli]`.")
    exit(1)


import ssdp


class PrintProcessor:
    """Print SSDP messages to stdout."""

    def process_request(self, request: ssdp.messages.SSDPRequest, addr: tuple):
        """Handle an incoming request."""
        self.pprint(request, addr)

    def process_response(self, response: ssdp.messages.SSDPResponse, addr: tuple):
        """Handle an incoming response."""
        self.pprint(response, addr)

    @staticmethod
    def pprint(msg, addr):
        """Pretty print the message."""
        host = f"[{addr[0]}]" if ":" in addr[0] else addr[0]
        host = click.style(host, fg="green", bold=True)
        port = click.style(str(addr[1]), fg="yellow", bold=True)
        click.echo(
            "%s:%s - - [%s] %s" % (host, port, time.asctime(), prettify_msg(msg))
        )


class PrintSSDMessageProtocol(
    PrintProcessor, ssdp.asyncio.SimpleServiceDiscoveryProtocol
):
    pass


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity.")
def cli(verbose):
    """SSDP command line interface."""
    logging.basicConfig(
        level=max(10, 10 * (2 - verbose)),
        format="%(levelname)s: [%(asctime)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


@cli.command()
@click.option(
    "--bind",
    "-b",
    help="Specify alternate bind address [default: all interfaces]",
)
def discover(bind):
    """Send out an M-SEARCH request and listening for responses."""
    family, addr = _get_best_family(bind, network.PORT)
    loop = asyncio.get_event_loop()

    connect = loop.create_datagram_endpoint(PrintSSDMessageProtocol, family=family)
    transport, protocol = loop.run_until_complete(connect)

    target = network.MULTICAST_ADDRESS_IPV4, network.PORT

    search_request = ssdp.messages.SSDPRequest(
        "M-SEARCH",
        headers={
            "HOST": "%s:%d" % target,
            "MAN": '"ssdp:discover"',
            "MX": "4",
            "ST": "ssdp:all",
        },
    )

    target = network.MULTICAST_ADDRESS_IPV4, network.PORT

    search_request.sendto(transport, target)

    PrintSSDMessageProtocol.pprint(search_request, addr[:2])
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        transport.close()


class PrintSSDPMessageHandler(PrintProcessor, SSDPMessageHandler):
    pass


@cli.command(name="server")
@click.option(
    "--bind",
    "-b",
    help="Specify alternate bind address [default: all interfaces]",
)
def serve(bind, ServerClass=SSDPServer):
    if platform.system() == "Darwin":
        # macOS doesn't support IPv6 multicast
        ServerClass.address_family, addr = _get_best_family(
            bind, network.PORT, socket.AF_INET
        )
    else:
        ServerClass.address_family, addr = _get_best_family(bind, network.PORT)

    with ServerClass(addr, PrintSSDPMessageHandler) as ssdpd:
        host, port = ssdpd.socket.getsockname()[:2]
        url_host = f"[{host}]" if ":" in host else host
        click.echo(
            f"Serving SSDP on {host} port {port} " f"(http://{url_host}:{port}/) ..."
        )
        try:
            ssdpd.serve_forever()
        except KeyboardInterrupt:
            click.echo("\nKeyboard interrupt received, exiting.")
            sys.exit(0)


if __name__ == "__main__":
    cli()
