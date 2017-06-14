import pytest


@pytest.fixture
def config(web_config, rabbit_config):
    config = {}
    config.update(web_config)
    config.update(rabbit_config)
    return config
