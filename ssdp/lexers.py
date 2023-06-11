from pygments import lexer, lexers, token


class SSDPLexer(lexers.HttpLexer):
    """Lexer for SSDP messages."""

    name = "SSDP"
    aliases = ["ssdp"]

    tokens = {
        "root": [
            (
                r"(M-SEARCH|NOTIFY)( +)([^ ]+)( +)"
                r"(HTTP)(/)(1\.[01]|2(?:\.0)?|3)(\r?\n|\Z)",
                lexer.bygroups(
                    token.Name.Function,
                    token.Text,
                    token.Name.Namespace,
                    token.Text,
                    token.Keyword.Reserved,
                    token.Operator,
                    token.Number,
                    token.Text,
                ),
                "headers",
            ),
            (
                r"(HTTP)(/)(1\.[01]|2(?:\.0)?|3)( +)(\d{3})(?:( +)([^\r\n]*))?(\r?\n|\Z)",
                lexer.bygroups(
                    token.Keyword.Reserved,
                    token.Operator,
                    token.Number,
                    token.Text,
                    token.Number,
                    token.Text,
                    token.Name.Exception,
                    token.Text,
                ),
                "headers",
            ),
        ],
        "headers": [
            (
                r"([^\s:]+)( *)(:)( *)([^\r\n]+)(\r?\n|\Z)",
                lexers.HttpLexer.header_callback,
            ),
            (
                r"([\t ]+)([^\r\n]+)(\r?\n|\Z)",
                lexers.HttpLexer.continuous_header_callback,
            ),
            (r"\r?\n", token.Text, "content"),
        ],
        "content": [(r".+", lexers.HttpLexer.content_callback)],
    }
