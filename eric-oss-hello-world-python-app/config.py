'''This module handles environment variables'''
import os

def get_config():
    '''
    get env and return config with all env vals required
    '''
    iam_client_id           = get_os_env_string("IAM_CLIENT_ID", "")
    iam_client_secret       = get_os_env_string("IAM_CLIENT_SECRET", "")
    iam_base_url            = get_os_env_string("IAM_BASE_URL", "")
    ca_cert_file_name       = get_os_env_string("CA_CERT_FILENAME", "")
    ca_mount_path           = get_os_env_string("CA_CERT_MOUNT_PATH", "")
    log_ctrl_file           = get_os_env_string("LOG_CTRL_FILE", "")
    log_endpoint            = get_os_env_string("LOG_ENDPOINT", "")
    log_tls_key             = get_os_env_string("APP_LOG_TLS_KEY", "")
    log_tls_cert            = get_os_env_string("APP_LOG_TLS_CERT", "")
    log_tls_ca_cert         = get_os_env_string("LOG_TLS_CA_CERT", "")
    log_ca_cert_file_path   = get_os_env_string("LOG_CA_CERT_FILE_PATH", "")
    rapp_log_cert_file_path = get_os_env_string("APP_LOG_CERT_FILE_PATH", "")

    config = {
            "iam_client_id": iam_client_id,
            "iam_client_secret": iam_client_secret,
            "iam_base_url": iam_base_url,
            "ca_cert_file_name": ca_cert_file_name,
            "ca_mount_path": ca_mount_path,
            "log_ctrl_file": log_ctrl_file,
            "log_endpoint": log_endpoint,
            "log_tls_key": log_tls_key,
            "log_tls_cert": log_tls_cert,
            "log_tls_ca_cert": log_tls_ca_cert,
            "log_ca_cert_file_path": log_ca_cert_file_path,
            "rapp_log_cert_file_path": rapp_log_cert_file_path
    }
    return config


def get_os_env_string(env_name, default_value):
    '''
    get env
    '''
    return os.getenv(env_name, default_value).strip()
