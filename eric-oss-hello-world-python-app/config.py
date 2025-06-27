"""This module handles environment variables"""

import os


def get_config():
    """get env and return config with all env vals required"""
    iam_client_id = get_os_env_string("IAM_CLIENT_ID", "")
    iam_client_secret = get_os_env_string("IAM_CLIENT_SECRET", "")
    iam_base_url = get_os_env_string("IAM_BASE_URL", "")
    ca_cert_file_name = get_os_env_string("CA_CERT_FILE_NAME", "")
    ca_cert_file_path = get_os_env_string("CA_CERT_FILE_PATH", "")
    log_ctrl_file = get_os_env_string("LOG_CTRL_FILE", "")
    log_endpoint = get_os_env_string("LOG_ENDPOINT", "")
    app_key = get_os_env_string("APP_KEY", "")
    app_cert = get_os_env_string("APP_CERT", "")
    app_cert_file_path = get_os_env_string("APP_CERT_FILE_PATH", "")
    client_creds_file_path = get_os_env_string("CLIENT_CREDS_FILE_PATH", "")
    client_id_file_name = get_os_env_string("CLIENT_ID_FILE_NAME", "")

    config = {
        "iam_client_id": iam_client_id,
        "iam_client_secret": iam_client_secret,
        "iam_base_url": iam_base_url,
        "ca_cert_file_name": ca_cert_file_name,
        "ca_cert_file_path": ca_cert_file_path,
        "log_ctrl_file": log_ctrl_file,
        "log_endpoint": log_endpoint,
        "app_key": app_key,
        "app_cert": app_cert,
        "app_cert_file_path": app_cert_file_path,
        "client_creds_file_path": client_creds_file_path,
        "client_id_file_name": client_id_file_name,
    }
    return config


def get_os_env_string(env_name, default_value):
    """get env"""
    return os.getenv(env_name, default_value).strip()
