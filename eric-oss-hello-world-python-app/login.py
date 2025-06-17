'''
This module performs client credentials grant authentication
by sending HTTP requests with TLS and with required environment
variables.
 '''
import os
from urllib.parse import urljoin
import json
import requests
import logging
import re
from config import get_config

class LoginError(Exception):
    """Raised when EIC login fails"""

def login():
    '''
    Get bearer token for accessing platform REST APIs:
    https://developer.intelligentautomationplatform.ericsson.net/#tutorials/app-authentication
    '''
    config = get_config()
    login_path = "/auth/realms/master/protocol/openid-connect/token"
    login_url = urljoin(config.get("iam_base_url"), login_path)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        resp = tls_login(login_url, headers)
    except LoginError as e:
        error_message = str(e)
        match = re.search(r'\((\d{3})\)', error_message)
        if match:
            status_code = int(match.group(1))
            print(f"Login failed with status code: {status_code}")
        else:
            print(f"Login failed: {error_message}")
        return None, 0

    resp = json.loads(resp.decode('utf-8'))
    token, time_until_expiry = resp["access_token"], resp["expires_in"]
    time_until_expiry -= 10 # add a buffer to ensure our session doesn't expire mid-request
    return token, time_until_expiry

def tls_login(url, headers):
    '''
    This function sends an HTTP POST request with TLS for the login operation
    '''
    config = get_config()
    ca_cert = os.path.join("/", config.get("ca_cert_file_path"), config.get("ca_cert_file_name"))
    app_cert = os.path.join("/", config.get("app_cert_file_path"), config.get("app_cert"))
    app_key = os.path.join("/", config.get("app_cert_file_path"), config.get("app_key"))
    authentication_type = config.get("authentication_type").lower()
    try:
        
        print("Headers:", headers)
        if authentication_type == "client-x509":
            print("client_creds_file_path:", config.get("client_creds_file_path"))
            print("client_id_file_name:", config.get("client_id_file_name"))
            client_id_file_path = os.path.join("/", config.get("client_creds_file_path"), config.get("client_id_file_name"))
            print("Hello 1:", client_id_file_path)
            client_id = read_file(client_id_file_path)
            print("Hello 2:", client_id)
            form_data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "tenant_id": "master"
            }
            print("Form data1:", form_data)
            print(f"Login1")
            response = requests.post(
                url,
                data=form_data,
                headers=headers,
                timeout=5,
                verify=ca_cert,
                cert=(app_cert, app_key)
            )
        elif authentication_type == "client-secret":
            form_data = {
                "grant_type": "client_credentials",
                "client_id": config.get("iam_client_id"),
                "client_secret": config.get("iam_client_secret"),
                "tenant_id": "master"
            }
            print("Form data2:", form_data)
            print(f"Login2")
            response = requests.post(
                url,
                data=form_data,
                headers=headers,
                timeout=5,
                verify=ca_cert
            )
        if response.status_code != 200:
            print(f"Log POST to https://{url} responded with {response.status_code}: {response.text}")
            print(f"Login3")
            print("Response status code:", response.status_code)
            print("Response content:", response.text)
            raise LoginError(f"Login failed ({response.status_code})")
    except Exception as exception:
        print(f"Login4")
        raise LoginError(f"Login failed ({exception})") from exception
    return response.content

def read_file(path):
    with open(path, "r") as f:
        return f.read().strip()
