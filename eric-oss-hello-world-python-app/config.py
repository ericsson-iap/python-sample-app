"""This module handles environment variables"""

import os


def get_config():
    """get env and return config with all env vals required"""
    eic_host_url = get_os_env_string("EIC_HOST_URL", "")
    ca_cert_file_name = get_os_env_string("CA_CERT_FILE_NAME", "")
    ca_cert_file_path = get_os_env_string("CA_CERT_FILE_PATH", "")
    log_ctrl_file = get_os_env_string("LOG_CTRL_FILE", "")
    log_endpoint = get_os_env_string("LOG_ENDPOINT", "")
    app_key = get_os_env_string("APP_KEY", "")
    app_cert = get_os_env_string("APP_CERT", "")
    app_cert_file_path = get_os_env_string("APP_CERT_FILE_PATH", "")
    client_creds_file_path = get_os_env_string("CLIENT_CREDS_FILE_PATH", "")
    client_id_file_name = get_os_env_string("CLIENT_ID_FILE_NAME", "")
    app_namespace = get_os_env_string("APP_NAMESPACE", "")

    config = {
        "eic_host_url": eic_host_url,
        "ca_cert_file_name": ca_cert_file_name,
        "ca_cert_file_path": ca_cert_file_path,
        "log_ctrl_file": log_ctrl_file,
        "log_endpoint": log_endpoint,
        "app_key": app_key,
        "app_cert": app_cert,
        "app_cert_file_path": app_cert_file_path,
        "client_creds_file_path": client_creds_file_path,
        "client_id_file_name": client_id_file_name,
        "chosen_unique_name": "eric-oss-hello-world-python-app",
        "app_namespace": app_namespace,
    }
    return config

def get_metrics_namespace(config):
    """Converts the chosen_unique_name to a valid Prometheus namespace"""
    return config.get("chosen_unique_name").replace("-", "_")

def get_os_env_string(env_name, default_value):
    """get env"""
    return os.getenv(env_name, default_value).strip()
