"""
This module performs client credentials grant authentication
by sending HTTP requests with TLS and with required environment
variables.
 """

import os
from urllib.parse import urljoin
import json
import requests
import time
from config import get_config


class LoginError(Exception):
    """Raised when EIC login fails"""


def login():
    """
    Get bearer token for accessing platform REST APIs:
    https://developer.intelligentautomationplatform.ericsson.net/#tutorials/app-authentication
    """
    config = get_config()
    login_path = "/auth/realms/master/protocol/openid-connect/token"
    login_url = urljoin(config.get("iam_base_url"), login_path)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = tls_login(login_url, headers)
    resp = json.loads(resp.decode("utf-8"))
    token, time_until_expiry = resp["access_token"], resp["expires_in"]
    time_until_expiry -= (
        10  # add a buffer to ensure our session doesn't expire mid-request
    )
    return token, time.time() + time_until_expiry


def tls_login(url, headers):
    """
    This function sends an HTTP POST request with TLS for the login operation
    """
    config = get_config()
    ca_cert = os.path.join(
        "/", config.get("ca_cert_file_path"), config.get("ca_cert_file_name")
    )
    app_cert = os.path.join(
        "/", config.get("app_cert_file_path"), config.get("app_cert")
    )
    app_key = os.path.join(
        "/", config.get("app_cert_file_path"), config.get("app_key"))
    client_id_path = os.path.join(
        "/", config.get("client_creds_file_path"), config.get("client_id_file_name")
    )
    form_data = {"grant_type": "client_credentials", "tenant_id": "master"}
    cert = (app_cert, app_key)

    try:
        with open(client_id_path, "r") as f:
            form_data["client_id"] = f.read().strip()
    except OSError as e:
        raise LoginError(f"Error while reading client id: {e}")
    
    try:
        response = requests.post(
            url, data=form_data, headers=headers, timeout=5, verify=ca_cert, cert=cert
        )
        if response.status_code != 200:
            raise LoginError(f"Login failed ({response.status_code})")
    except Exception as exception:
        raise LoginError(f"Login failed ({exception})") from exception
    return response.content
