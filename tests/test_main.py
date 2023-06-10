import importlib

import pytest


@pytest.mark.cli
class TestDiscover:
    def test_help(self):
        main = pytest.importorskip("ssdp.__main__")
        testing = pytest.importorskip("click.testing")
        results = testing.CliRunner().invoke(main.ssdp, ["discover", "--help"])
        assert results.exit_code == 0
        assert "Usage: ssdp discover [OPTIONS]" in results.output

    def test_call(self):
        main = pytest.importorskip("ssdp.__main__")
        testing = pytest.importorskip("click.testing")
        results = testing.CliRunner().invoke(main.ssdp, ["discover", "--max-wait", "1"])
        assert results.exit_code == 0
        assert "ssdp:all" in results.output

    def test_call_w_search_target(self):
        main = pytest.importorskip("ssdp.__main__")
        testing = pytest.importorskip("click.testing")
        results = testing.CliRunner().invoke(
            main.ssdp, ["discover", "--max-wait", "1", "--search-target", "ssdp:dial"]
        )
        assert results.exit_code == 0
        assert "ssdp:dial" in results.output


@pytest.mark.skipif(
    importlib.util.find_spec("pygments") is not None, reason="cli is installed"
)
def test_import_warning():
    with pytest.raises(ImportError) as e:
        importlib.import_module("ssdp.__main__")

    assert (
        "The SSDP CLI requires needs to be installed via `pip install ssdp[cli]`."
        in str(e.value)
    )
