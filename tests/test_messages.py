from unittest.mock import Mock

import pytest
from ssdp import network
from ssdp.messages import SSDPMessage, SSDPRequest, SSDPResponse

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

    def test_parse(self):
        assert isinstance(SSDPMessage.parse("HTTP/1.1 200 OK"), SSDPResponse)
        assert isinstance(SSDPMessage.parse("NOTIFY * HTTP/1.1"), SSDPRequest)

    def test_parse_headers(self):
        headers = SSDPMessage.parse_headers("Cache-Control: max-age=3600")
        assert headers == [("Cache-Control", "max-age=3600")]

    def test_str(self):
        with pytest.raises(NotImplementedError):
            str(SSDPMessage())

    def test_bytes(self):
        class MyMessage(SSDPMessage):
            def __str__(self):
                return "NOTIFY * HTTP/1.1\r\nCache-Control: max-age=3600"

        msg = MyMessage()
        assert bytes(msg) == (
            b"NOTIFY * HTTP/1.1\r\nCache-Control: max-age=3600\r\n\r\n"
        )


class TestSSDPResponse:
    def test_parse(self):
        response = SSDPResponse.parse(fixtures.response.decode())
        assert response.status_code == 200
        assert response.reason == "OK"

    def test_str(self):
        response = SSDPResponse(
            200, "OK", headers=[("Location", "http://192.168.1.239:55443")]
        )
        assert str(response) == (
            "HTTP/1.1 200 OK\r\nLocation: http://192.168.1.239:55443"
        )

    def test_sendto(self):
        transport = Mock()
        addr = network.MULTICAST_ADDRESS_IPV4, network.PORT
        SSDPResponse(
            200, "OK", headers=[("Location", "http://192.168.1.239:55443")]
        ).sendto(transport, addr)
        transport.sendto.assert_called_once_with(
            b"HTTP/1.1 200 OK\r\nLocation: http://192.168.1.239:55443\r\n\r\n", addr
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
        assert str(request) == ("NOTIFY * HTTP/1.1\r\nCache-Control: max-age=3600")

    def test_sendto(self):
        transport = Mock()
        addr = network.MULTICAST_ADDRESS_IPV4, network.PORT
        SSDPRequest("NOTIFY", "*").sendto(transport, addr)
        transport.sendto.assert_called_once_with(b"NOTIFY * HTTP/1.1\r\n\r\n", addr)
