"""This module handles mTLS logging"""

import json
import os
import logging
import sys
from enum import IntEnum
from datetime import datetime, timezone
import requests
from config import get_config, get_os_env_string


class Severity(IntEnum):
    """We use this to map the logging library severity to the mTLS logging"""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


# pylint: disable=too-few-public-methods
class MtlsLogging:
    """mTLS logger which will log to STDOUT, as well as Log Aggregator"""

    def __init__(self, level=None):
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.ERROR)
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)

        if not level:
            # Set a default level if logger is not initialized with one
            level = Severity.INFO
            if self.config["log_ctrl_file"]:
                # If level is defined in charts\eric-oss-hello-world-python-app\logcontrol.json
                with open(
                    self.config["log_ctrl_file"], "r", encoding="utf-8"
                ) as log_ctrl_file:
                    log_ctrl = json.load(log_ctrl_file)
                    container_name = get_os_env_string("CONTAINER_NAME", "")
                    for obj in log_ctrl:
                        if obj["container"] == container_name:
                            log_ctrl = obj
                            break
                    if log_ctrl["severity"] == "critical":
                        level = Severity.CRITICAL
                    elif log_ctrl["severity"] == "error":
                        level = Severity.ERROR
                    elif log_ctrl["severity"] == "warning":
                        level = Severity.WARNING

        self.logger.setLevel(level)
        handler.setLevel(level)
        self.logger.addHandler(handler)
        self.log(f"Level set to: {level}", Severity.INFO)

    def log(self, message, severity):
        """Send request to log aggregator with mTLS"""
        # Determine if certs are set.
        cert_available = (
            self.config.get("ca_cert_file_name") != ""
            and self.config.get("ca_cert_file_path") != ""
            and self.config.get("app_cert") != ""
            and self.config.get("app_key") != ""
            and self.config.get("app_cert_file_path") != ""
        )

        log_url = self.config.get("log_endpoint")
        time = datetime.now(timezone.utc).isoformat()

        headers = {"Content-Type": "application/json"}
        json_data = {
            "timestamp": time,
            "version": "0.0.1",
            "message": message,
            "service_id": "rapp-eric-oss-hello-world-python-app",
            "severity": severity.name.lower(),
        }

        # print to console
        self.logger.log(severity, message)

        if not cert_available:
            missing_parameters = "Missing TLS logging additional parameter(s): "
            for k, v in self.config.items():
                if v == "":
                    missing_parameters += k + " "

            self.logger.error(missing_parameters)
        elif severity >= self.logger.getEffectiveLevel():
            # send log to log transformer
            try:
                ca_cert = os.path.join(
                    "/",
                    self.config.get("ca_cert_file_path"),
                    self.config.get("ca_cert_file_name"),
                )
                app_cert = os.path.join(
                    "/",
                    self.config.get("app_cert_file_path"),
                    self.config.get("app_cert"),
                )
                app_key = os.path.join(
                    "/",
                    self.config.get("app_cert_file_path"),
                    self.config.get("app_key"),
                )
                requests.post(
                    f"https://{log_url}",
                    json=json_data,
                    timeout=5,
                    headers=headers,
                    verify=ca_cert,
                    cert=(app_cert, app_key),
                )
            except (
                requests.exceptions.InvalidURL,
                requests.exceptions.MissingSchema,
            ) as exception:
                # logs to console if failed to log to log transformer
                self.logger.error("Request failed for mTLS logging: %s", exception)
