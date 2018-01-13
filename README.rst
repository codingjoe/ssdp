Python SSDP
===========

|version| |ci| |coverage| |license|

Python asyncio library for Simple Service Discovery Protocol (SSDP).

SSDP is a UPnP sub standard. For more information see: https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol

Setup
-----

.. code:: shell

    pip install ssdp


Usage
-----

.. code:: python

    import asyncio
    import ssdp


    class MyProtocol(ssdp.SimpleServiceDiscoveryProtocol):

        def response_received(self, response, addr):
            print(response, addr)

        def request_received(self, request, addr):
            print(request, addr)


    loop = asyncio.get_event_loop()
    connect = loop.create_datagram_endpoint(MyProtocol, family=socket.AF_INET)
    transport, protocol = loop.run_until_complete(connect)

    notify = ssdp.SSDPRequest('NOTIFY')
    notify.sendto(transport, (MyProtocol.MULTICAST_ADDRESS, 1982))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()

.. |version| image:: https://img.shields.io/pypi/v/ssdp.svg
    :target: https://pypi.python.org/pypi/ssdp/
.. |ci| image:: https://api.travis-ci.org/codingjoe/ssdp.svg?branch=master
    :target: https://travis-ci.org/codingjoe/ssdp
.. |coverage| image:: https://codecov.io/gh/codingjoe/ssdp/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/codingjoe/ssdp
.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: LICENSE
