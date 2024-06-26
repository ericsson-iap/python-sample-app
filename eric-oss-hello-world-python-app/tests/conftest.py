'''
Configure a Flask fixture based off the Application defined in main.py
'''

import os
import pytest
import requests_mock
from prometheus_client import REGISTRY as GLOBAL_METRICS_REGISTRY
from main import Application
from config import get_config

def pytest_generate_tests():
    '''Override environment variables to simulate instantiation with these values set'''
    os.environ["IAM_CLIENT_ID"] = "IAM_CLIENT_ID"
    os.environ["IAM_CLIENT_SECRET"] = "IAM_CLIENT_SECRET"
    os.environ["IAM_BASE_URL"] = "https://www.iam-base-url.com"
    os.environ["CA_CERT_FILENAME"] = "CA_CERT_FILENAME"
    os.environ["CA_CERT_MOUNT_PATH"] = "CA_CERT_MOUNT_PATH"
    os.environ["LOG_ENDPOINT"] = "LOG_ENDPOINT"
    os.environ["APP_LOG_TLS_KEY"] = "APP_LOG_TLS_KEY"
    os.environ["APP_LOG_TLS_CERT"] = "APP_LOG_TLS_CERT"
    os.environ["LOG_TLS_CA_CERT"] = "LOG_TLS_CA_CERT"
    os.environ["LOG_CA_CERT_FILE_PATH"] = "LOG_CA_CERT_FILE_PATH"
    os.environ["APP_LOG_CERT_FILE_PATH"] = "APP_LOG_CERT_FILE_PATH"

@pytest.fixture(name="mock_log_api")
def fixture_mock_log_api(config):
    log_endpoint = f"https://{config.get('log_endpoint')}"
    with requests_mock.Mocker() as request_mocker:
        request_mocker.post(log_endpoint)
        yield request_mocker


@pytest.fixture(name="app")
def fixture_app(mock_log_api):

    # pylint: disable=unused-argument
    '''Create a fixture out of our Application, which will be used by any test_*.py file'''
    application = Application()
    application.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield application
    GLOBAL_METRICS_REGISTRY.unregister(application.requests_total)
    GLOBAL_METRICS_REGISTRY.unregister(application.requests_failed)


    # clean up / reset resources here


@pytest.fixture()
def client(app):
    '''Every time a test wants a client, give it a new copy of our Application'''
    return app.test_client()


@pytest.fixture(name="config")
def fixture_config():
    '''Every time a test wants a config, give it a stub'''
    return get_config()

@pytest.fixture(scope="function")
def no_log_certs():
    os.environ["APP_LOG_TLS_KEY"] = ""
    os.environ["APP_LOG_TLS_CERT"] = ""
    os.environ["LOG_TLS_CA_CERT"] = ""
    os.environ["LOG_CA_CERT_FILE_PATH"] = ""
    os.environ["APP_LOG_CERT_FILE_PATH"] = ""
    yield
    os.environ["APP_LOG_TLS_KEY"] = "APP_LOG_TLS_KEY"
    os.environ["APP_LOG_TLS_CERT"] = "APP_LOG_TLS_CERT"
    os.environ["LOG_TLS_CA_CERT"] = "LOG_TLS_CA_CERT"
    os.environ["LOG_CA_CERT_FILE_PATH"] = "LOG_CA_CERT_FILE_PATH"
    os.environ["APP_LOG_CERT_FILE_PATH"] = "APP_LOG_CERT_FILE_PATH"
