"""Tests which ensure the application handles Authentication & Authorisation properly"""
from urllib.parse import urljoin
import time
from login import login, LoginError
import pytest

def test_login_receives_token_x509(mock_login_api, config):
    """Check if we receive a token"""
    token, expiry = login()
    assert token == "2YotnFZFEjr1zCsicMWpAA" and expiry > time.time()


def test_login_bad_credentials(requests_mock, config):
    """Ensure we get an error if credentials are bad"""
    login_url = urljoin(
        config.get("iam_base_url"), "/auth/realms/master/protocol/openid-connect/token"
    )
    requests_mock.post(
        login_url, status_code=400, json={"error": "invalid_request"}
    )  # Example reply from OAuth2 spec: https://datatracker.ietf.org/doc/html/rfc6749#section-5.2
    with pytest.raises(LoginError) as e:
        login()
        assert "400" in e
