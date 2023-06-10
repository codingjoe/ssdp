import pytest


@pytest.mark.cli
class TestSSDPLexer:
    def test_plugin_registry(self):
        pygments = pytest.importorskip("pygments")
        lexers = pytest.importorskip("ssdp.lexers")

        assert isinstance(pygments.lexers.get_lexer_by_name("ssdp"), lexers.SSDPLexer)

    def test_tokens(self):
        pygments = pytest.importorskip("pygments")
        lexers = pytest.importorskip("ssdp.lexers")

        lexer = lexers.SSDPLexer()
        text = "M-SEARCH * HTTP/1.1\r\n" "HOST: example.com:1900\r\n"
        tokens = list(lexer.get_tokens(text))
        assert tokens == [
            (pygments.token.Token.Name.Function, "M-SEARCH"),
            (pygments.token.Token.Text, " "),
            (pygments.token.Token.Name.Namespace, "*"),
            (pygments.token.Token.Text, " "),
            (pygments.token.Token.Keyword.Reserved, "HTTP"),
            (pygments.token.Token.Operator, "/"),
            (pygments.token.Token.Literal.Number, "1.1"),
            (pygments.token.Token.Text, "\n"),
            (pygments.token.Token.Name.Attribute, "HOST"),
            (pygments.token.Token.Text, ""),
            (pygments.token.Token.Operator, ":"),
            (pygments.token.Token.Text, " "),
            (pygments.token.Token.Literal, "example.com:1900"),
            (pygments.token.Token.Text, "\n"),
        ]
