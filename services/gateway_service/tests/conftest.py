import pytest
from src import create_app
from src.config import Config


class TestConfig(Config):
    TESTING = True
    # Add test-specific configuration here


@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture
def client(app):
    return app.test_client()
