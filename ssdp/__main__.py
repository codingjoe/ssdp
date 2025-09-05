#!/usr/bin/env python3
import asyncio
import logging
import time

from ssdp import messages, network
from ssdp.aio import SSDP

try:
    import click
    from pygments import formatters, highlight

    from .lexers import SSDPLexer
except ImportError as e:
    raise ImportError(
        "The SSDP CLI requires needs to be installed via `pip install ssdp[cli]`."
    ) from e


class ConsoleMessageProcessor:
    """Print SSDP messages to stdout."""

    def request_received(self, request: messages.SSDPRequest, addr: tuple):
        self.pprint(request, addr)

    def response_received(self, response: messages.SSDPResponse, addr: tuple):
        self.pprint(response, addr)

    @staticmethod
    def pprint(msg, addr):
        """Pretty print the message."""
        host = f"[{addr[0]}]" if ":" in addr[0] else addr[0]
        host = click.style(host, fg="green", bold=True)
        port = click.style(str(addr[1]), fg="yellow", bold=True)
        pretty_msg = highlight(str(msg), SSDPLexer(), formatters.TerminalFormatter())
        click.echo(f"{host}:{port} - - [{time.asctime()}] {pretty_msg}")


class PrintSSDMessageProtocol(ConsoleMessageProcessor, SSDP):
    pass


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity.")
def ssdp(verbose):
    """SSDP command line interface."""
    logging.basicConfig(
        level=max(10, 10 * (2 - verbose)),
        format="%(levelname)s: [%(asctime)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


@ssdp.command()
@click.option(
    "--bind",
    "-b",
    help="Specify alternate bind address [default: all interfaces]",
)
@click.option(
    "--search-target",
    "--st",
    default="ssdp:all",
    help="Search target [default: ssdp:all]",
)
@click.option(
    "--max-wait",
    "--mx",
    default=5,
    help="Maximum wait time in seconds [default: 5]",
)
def discover(bind, search_target, max_wait):
    """Send out an M-SEARCH request and listening for responses."""
    family, addr = network.get_best_family(bind, network.PORT)
    loop = asyncio.get_event_loop()

    connect = loop.create_datagram_endpoint(PrintSSDMessageProtocol, family=family)
    transport, protocol = loop.run_until_complete(connect)

    search_request = messages.SSDPRequest(
        "M-SEARCH",
        headers={
            "HOST": f"{network.MULTICAST_ADDRESS_IPV4}:{network.PORT:d}",
            "MAN": '"ssdp:discover"',
            "MX": str(max_wait),  # seconds to delay response [1..5]
            "ST": search_target,
        },
    )

    search_request.sendto(transport, (network.MULTICAST_ADDRESS_IPV4, network.PORT))

    PrintSSDMessageProtocol.pprint(search_request, addr[:2])
    try:
        loop.run_until_complete(asyncio.sleep(4))
    finally:
        transport.close()


if __name__ == "__main__":  # pragma: no cover
    ssdp()
