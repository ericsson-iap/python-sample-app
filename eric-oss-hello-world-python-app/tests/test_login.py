'''Tests which ensure the application handles Authentication & Authorisation properly'''
from urllib.parse import urljoin
from login import login


def test_login_receives_token(requests_mock, config):
    '''Check if we receive a token'''
    login_url = urljoin(config.get("iam_base_url"), "/auth/realms/master/protocol/openid-connect/token")
    requests_mock.post(login_url, json = {
       "access_token":"2YotnFZFEjr1zCsicMWpAA",
       "token_type":"example",
       "expires_in":3600,
       "example_parameter":"example_value"
     }) # Example reply from OAuth2 spec: https://datatracker.ietf.org/doc/html/rfc6749#section-4.4.3
    token, expiry = login()
    assert token == "2YotnFZFEjr1zCsicMWpAA" and expiry + 10 == 3600


def test_login_bad_credentials(requests_mock, config):
    '''Ensure we get an error if credentials are bad'''
    login_url = urljoin(config.get("iam_base_url"), "/auth/realms/master/protocol/openid-connect/token")
    requests_mock.post(login_url, status_code=400, json = {
       "error":"invalid_request"
     }) # Example reply from OAuth2 spec: https://datatracker.ietf.org/doc/html/rfc6749#section-5.2
    token, expiry = login()
    assert not token and expiry == 0
