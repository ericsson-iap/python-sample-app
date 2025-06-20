"""
Configure a Flask fixture based off the Application defined in main.py
"""

import os
import pytest
import requests_mock
from prometheus_client import REGISTRY as GLOBAL_METRICS_REGISTRY
from urllib.parse import urljoin
from main import Application
from config import get_config


def pytest_generate_tests():
    populate_environment_variables()


@pytest.fixture(name="mock_log_api")
def fixture_mock_log_api(config):
    log_endpoint = f"https://{config.get('log_endpoint')}"
    with requests_mock.Mocker() as request_mocker:
        request_mocker.post(log_endpoint)
        yield request_mocker


def match_request_data(request):
    uses_x509 = request.cert and all(
        [
            parameter in request.text
            for parameter in [
                "grant_type=client_credentials",
                "tenant_id=master",
                "client_id=IAM_CLIENT_ID",
            ]
        ]
    )
    uses_legacy = all(
        [
            parameter in request.text
            for parameter in [
                "grant_type=client_credentials",
                "tenant_id=master",
                "client_id=IAM_CLIENT_ID",
                "client_secret=IAM_CLIENT_SECRET",
            ]
        ]
    )
    return uses_x509 or uses_legacy


@pytest.fixture(name="mock_login_api")
def fixture_mock_login_api(config):
    login_endpoint = urljoin(
        config.get("iam_base_url"), "/auth/realms/master/protocol/openid-connect/token"
    )
    with requests_mock.Mocker() as request_mocker:
        request_mocker.post(
            login_endpoint,
            request_headers={"Content-Type": "application/x-www-form-urlencoded"},
            additional_matcher=match_request_data,
            json={
                "access_token": "2YotnFZFEjr1zCsicMWpAA",
                "token_type": "example",
                "expires_in": 3600,
                "example_parameter": "example_value",
            },
        )  # Example reply from OAuth2 spec: https://datatracker.ietf.org/doc/html/rfc6749#section-4.4.3
        yield request_mocker


@pytest.fixture(name="app")
def fixture_app(mock_log_api):

    # pylint: disable=unused-argument
    """Create a fixture out of our Application, which will be used by any test_*.py file"""
    application = Application()
    application.config.update(
        {
            "TESTING": True,
        }
    )

    # Why 'yield'? See: https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#dynamic-scope
    yield application
    GLOBAL_METRICS_REGISTRY.unregister(application.requests_total)
    GLOBAL_METRICS_REGISTRY.unregister(application.requests_failed)


@pytest.fixture()
def client(app):
    """Every time a test wants a client, give it a new copy of our Application"""
    return app.test_client()


@pytest.fixture(name="config")
def fixture_config():
    """Every time a test wants a config, give it a stub"""
    return get_config()


@pytest.fixture(scope="function")
def no_log_certs():
    # Remove references to log certs to simulate them being undefined.
    # This would simulate a user not setting these at instantiation time.
    os.environ["APP_KEY"] = ""
    os.environ["APP_CERT"] = ""
    os.environ["APP_CERT_FILE_PATH"] = ""

    # Why 'yield'? See: https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#dynamic-scope
    yield
    populate_environment_variables()


@pytest.fixture(scope="function")
def legacy_authentication():
    os.environ["AUTHENTICATION_TYPE"] = "legacy-client-secret"
    yield
    populate_environment_variables()


def populate_environment_variables():
    os.environ["IAM_CLIENT_ID"] = "IAM_CLIENT_ID"
    os.environ["IAM_CLIENT_SECRET"] = "IAM_CLIENT_SECRET"
    os.environ["IAM_BASE_URL"] = "https://www.iam-base-url.com"
    os.environ["CA_CERT_FILE_NAME"] = "CA_CERT_FILE_NAME"
    os.environ["CA_CERT_FILE_PATH"] = "CA_CERT_MOUNT_PATH"
    os.environ["LOG_ENDPOINT"] = "LOG_ENDPOINT"
    os.environ["APP_KEY"] = "APP_KEY"
    os.environ["APP_CERT"] = "APP_CERT"
    os.environ["APP_CERT_FILE_PATH"] = "APP_CERT_FILE_PATH"
    os.environ["AUTHENTICATION_TYPE"] = "client-x509"
    os.environ["CLIENT_CREDS_FILE_PATH"] = "/eric-oss-hello-world-python-app/tests/"
    os.environ["CLIENT_ID_FILE_NAME"] = "client_id_example"
