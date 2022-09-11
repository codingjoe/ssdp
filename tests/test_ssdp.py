import asyncio
import socket

import pytest

from ssdp import (
    SimpleServiceDiscoveryProtocol,
    SSDPMessage,
    SSDPRequest,
    SSDPResponse,
    UnexpectedMessage,
)

from . import fixtures


class TestSSDPMessage:
    def test_headers_copy(self):
        headers = [("Cache-Control", "max-age=3600")]
        msg = SSDPMessage(headers=headers)
        assert msg.headers == headers
        assert msg.headers is not headers

    def test_headers_dict(self):
        headers = {"Cache-Control": "max-age=3600"}
        msg = SSDPMessage(headers=headers)
        assert msg.headers == [("Cache-Control", "max-age=3600")]

    def test_headers_none(self):
        msg = SSDPMessage(headers=None)
        assert msg.headers == []

    def test_parse__empty(self):
        with pytest.raises(UnexpectedMessage) as e:
            SSDPMessage.parse("")
        assert str(e.value) == "Empty message"

    def test_parse__unexpected(self):
        with pytest.raises(UnexpectedMessage) as e:
            SSDPMessage.parse("asdf")
        assert str(e.value) == "Invalid request: asdf"

    def test_parse_headers(self):
        headers = SSDPMessage.parse_headers("Cache-Control: max-age=3600")
        assert headers == [("Cache-Control", "max-age=3600")]

    def test_str(self):
        with pytest.raises(NotImplementedError):
            str(SSDPMessage())

    def test_bytes(self):
        class MyMessage(SSDPMessage):
            def __str__(self):
                return "NOTIFY * HTTP/1.1\n" "Cache-Control: max-age=3600"

        msg = MyMessage()
        assert bytes(msg) == (b"NOTIFY * HTTP/1.1\r\n" b"Cache-Control: max-age=3600")


class TestSSDPResponse:
    def test_parse(self):
        response = SSDPResponse.parse(fixtures.response.decode())
        assert response.status_code == 200
        assert response.reason == "OK"

    def test_str(self):
        response = SSDPResponse(
            200, "OK", headers=[("Location", "Location: http://192.168.1.239:55443")]
        )
        assert str(response) == (
            "HTTP/1.1 200 OK\n" "Location: Location: http://192.168.1.239:55443"
        )


class TestSSDPRequest:
    def test_parse(self):
        request = SSDPRequest.parse(fixtures.request.decode())
        assert request.method == "NOTIFY"
        assert request.uri == "*"

    def test_str(self):
        request = SSDPRequest(
            "NOTIFY", "*", headers=[("Cache-Control", "max-age=3600")]
        )
        assert str(request) == ("NOTIFY * HTTP/1.1\n" "Cache-Control: max-age=3600")

    def test_sendto(self):
        requests = []

        class MyProtocol(SimpleServiceDiscoveryProtocol):
            def response_received(self, response, addr):
                print(response, addr)

            def request_received(self, request, addr):
                requests.append(request)
                print(request, addr)

        loop = asyncio.get_event_loop()
        connect = loop.create_datagram_endpoint(MyProtocol, family=socket.AF_INET)
        transport, protocol = loop.run_until_complete(connect)

        async def send_notify(transport):
            while True:
                notify = SSDPRequest("NOTIFY")
                notify.sendto(transport, (MyProtocol.MULTICAST_ADDRESS, 1982))
                await asyncio.sleep(1)

        loop.create_task(send_notify(transport))

        loop.run_until_complete(asyncio.sleep(3))
        transport.close()
        loop.close()
