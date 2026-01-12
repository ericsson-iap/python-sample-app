"""
This module performs client credentials grant authentication
by sending HTTP requests with TLS and with required environment
variables.
 """

import os
import json
import time
import requests
from urllib.parse import urljoin
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

    # Envoy outbound listener
    envoy_base_url = "http://127.0.0.1:9000"
    login_url = urljoin(envoy_base_url, login_path)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    form_data = {
        "grant_type": "client_credentials",
        "tenant_id": "master",
    }

    client_id_path = os.path.join(
        "/", config.get("client_creds_file_path"), config.get("client_id_file_name")
    )

    try:
        with open(client_id_path, "r", encoding="utf-8") as f:
            form_data["client_id"] = f.read().strip()
    except OSError as e:
        raise LoginError(f"Error while reading client id: {e}") from e

    try:
        response = requests.post(
            login_url,
            data=form_data,
            headers=headers,
            timeout=5,
        )

        if response.status_code != 200:
            raise LoginError(
                f"Login failed ({response.status_code}): {response.text}"
            )

    except Exception as exception:
        raise LoginError(f"Login failed ({exception})") from exception

    resp = response.json()

    token = resp["access_token"]
    time_until_expiry = resp["expires_in"]

    # buffer to avoid expiry mid-request
    time_until_expiry -= 10

    return token, time.time() + time_until_expiry
