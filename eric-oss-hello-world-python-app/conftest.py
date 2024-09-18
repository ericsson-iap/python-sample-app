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
    populate_environment_variables()

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

    # Why 'yield'? See: https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#dynamic-scope
    yield application 
    GLOBAL_METRICS_REGISTRY.unregister(application.requests_total)
    GLOBAL_METRICS_REGISTRY.unregister(application.requests_failed)


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
    # Remove references to log certs to simulate them being undefined.
    # This would simulate a user not setting these at instantiation time.
    os.environ["APP_KEY"] =             ""
    os.environ["APP_CERT"] =            ""
    os.environ["APP_CERT_FILE_PATH"] =  ""
    
    # Why 'yield'? See: https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#dynamic-scope
    yield
    populate_environment_variables()


def populate_environment_variables():
    os.environ["IAM_CLIENT_ID"] =           "IAM_CLIENT_ID"
    os.environ["IAM_CLIENT_SECRET"] =       "IAM_CLIENT_SECRET"
    os.environ["IAM_BASE_URL"] =            "https://www.iam-base-url.com"
    os.environ["CA_CERT_FILE_NAME"] =       "CA_CERT_FILE_NAME"
    os.environ["CA_CERT_FILE_PATH"] =       "CA_CERT_MOUNT_PATH"
    os.environ["LOG_ENDPOINT"] =            "LOG_ENDPOINT"
    os.environ["APP_KEY"] =                 "APP_KEY"
    os.environ["APP_CERT"] =                "APP_CERT"
    os.environ["APP_CERT_FILE_PATH"] =      "APP_CERT_FILE_PATH"