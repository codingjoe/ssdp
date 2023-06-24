def pytest_configure(config):
    config.addinivalue_line("markers", "cli: skip if selenium is not installed")
