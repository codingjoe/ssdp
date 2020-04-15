Python SSDP
===========

Python asyncio library for Simple Service Discovery Protocol (SSDP).

SSDP is a UPnP sub standard. For more information see: https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol

Setup
-----

.. code:: shell

    python3 -m pip install ssdp


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
