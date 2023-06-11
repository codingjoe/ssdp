# Python SSDP

Python asyncio library for Simple Service Discovery Protocol (SSDP).

SSDP is a UPnP substandard. For more information see:
https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol

## Setup

```bash
python3 -m pip install ssdp # lightweight, without any dependencies
# or
python3 -m pip install ssdp[cli] # with cli support for testing and debugging
```

## Usage

### CLI

```console-interactive
$ ssdp --help
Usage: ssdp [OPTIONS] COMMAND [ARGS]...

  SSDP command line interface.

Options:
  -v, --verbose  Increase verbosity.
  --help         Show this message and exit.

Commands:
  discover  Send out an M-SEARCH request and listening for responses.
```

#### Discover

Discover devices on the network and print the responses.

```console
ssdp discover --help
Usage: ssdp discover [OPTIONS]

  Send out an M-SEARCH request and listening for responses.

Options:
  -b, --bind TEXT             Specify alternate bind address [default: all
                              interfaces]
  --search-target, --st TEXT  Search target [default: ssdp:all]
  --max-wait, --mx INTEGER    Maximum wait time in seconds [default: 5]
  --help                      Show this message and exit.
```

Example:

```console
$ ssdp discover
[::]:1900 - - [Sun Jun 11 12:07:09 2023] M-SEARCH * HTTP/1.1
HOST: 239.255.255.250:1900
MAN: "ssdp:discover"
MX: 5
ST: ssdp:all

[::ffff:192.168.178.1]:1900 - - [Sun Jun 11 12:07:09 2023] HTTP/1.1 200 OK
Cache-Control: max-age=1800
Location: http://192.168.178.1:49000/MediaServerDevDesc.xml
Server: FRITZ!Box 7590 UPnP/1.0 AVM FRITZ!Box 7590 154.07.50
Ext:
ST: upnp:rootdevice
USN: uuid:fa095ecc-e13e-40e7-8e6c-3ca62f98471f::upnp:rootdevice
```

### Python API

#### Messages

The SSDP library provides two classes for SSDP messages: `SSDPRequest` and
`SSDPResponse`. Both classes are subclasses of `SSDPMessage` and provide
the following methods:

- `parse`: Parse a SSDP message from a string.
- `__bytes__`: Convert the SSDP message to a bytes object.
- `__str__`: Convert the SSDP message to a string.

You can parse a SSDP message from a string with the `parse` method.
It will return a `SSDPRequest` or `SSDPResponse` object depending
on the message type.

```pycon
>>> import ssdp.messages
>>> ssdp.messages.SSDPRequest.parse('NOTIFY * HTTP/1.1\r\n\r\n')
<ssdp.messages.SSDPRequest object at 0x7f8b1c0b6a90>
>>> ssdp.messages.SSDPResponse.parse('HTTP/1.1 200 OK\r\n\r\n')
<ssdp.messages.SSDPResponse object at 0x7f8b1c0b6a90>
```

##### SSDPRequest

```pycon
>>> from ssdp.messages import SSDPRequest
>>> SSDPRequest('NOTIFY', headers={
...     'HOST': '10.0.0.42',
...     'NT': 'upnp:rootdevice',
...     'NTS': 'ssdp:alive',
... })
<ssdp.messages.SSDPRequest object at 0x7f8b1c0b6a90>
```

The `SSDPRequest` class provides the a `sendto` method to send the request
over a open transport.

```pycon
>>> from ssdp import network, messages
>>> notify = messages.SSDPRequest('NOTIFY')
>>> notify.sendto(transport, (network.MULTICAST_ADDRESS_IPV4, network.PORT))
```

##### SSDPResponse

```pycon
>>> from ssdp.messages import SSDPResponse
>>> SSDPResponse(200, 'OK', headers={
...     'CACHE-CONTROL': 'max-age=1800',
...     'LOCATION': 'http://10.0.0.1:80/description.xml',
...     'SERVER': 'Linux/2.6.18 UPnP/1.0 quick_ssdp/1.0',
...     'ST': 'upnp:rootdevice',
... })
<ssdp.messages.SSDPResponse object at 0x7f8b1c0b6a90>
```

#### Asyncio SSD Protocol datagram endpoint

The `aio.SimpleServiceDiscoveryProtocol` class is a subclass of
`asyncio.DatagramProtocol` and provides the following additional methods:

- `response_received`: Called when a SSDP response was received.
- `request_received`: Called when a SSDP request was received.

The protocol can be used to react to SSDP messages in an asyncio event loop.

This example sends a SSDP NOTIFY message and prints all received SSDP messages:

```python
#!/usr/bin/env python3
import asyncio
import socket

from ssdp import aio, messages, network


class MyProtocol(aio.SimpleServiceDiscoveryProtocol):

  def response_received(self, response, addr):
    print(response, addr)

  def request_received(self, request, addr):
    print(request, addr)


loop = asyncio.get_event_loop()
connect = loop.create_datagram_endpoint(MyProtocol, family=socket.AF_INET)
transport, protocol = loop.run_until_complete(connect)

notify = messages.SSDPRequest('NOTIFY')
notify.sendto(transport, (network.MULTICAST_ADDRESS_IPV4, network.PORT))

try:
  loop.run_forever()
except KeyboardInterrupt:
  pass

transport.close()
loop.close()
```

## SSDP lexer plugin for [Pygments][pygments]

The SSDP library comes with a lexer plugin for [Pygments][pygments]
to highlight SSDP messages. It's based on a HTTP lexer and adds SSDP
specific keywords.

You can install the plugin with the following command:

```bash
pip install ssdp[pymgments]  # included in ssdp[cli]
```

You can either get the lexer by name:

```pycon
>>> from pygments.lexers import get_lexer_by_name
>>> get_lexer_by_name('ssdp')
<pygments.lexers.SSDPLexer>
```

Highlighting a SSDP message, could look like this:

```python
#/usr/bin/env python3
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter


if __name__ == '__main__':
    lexer = get_lexer_by_name('ssdp')
    formatter = TerminalFormatter()
    code = 'NOTIFY * HTTP/1.1\r\nHOST: localhost:1900'
    msg = highlight(code, lexer, formatter)
    print(msg)
```

[pygments]: https://pygments.org/
