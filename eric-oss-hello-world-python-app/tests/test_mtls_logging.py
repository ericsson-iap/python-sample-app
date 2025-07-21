"""Tests which cover the app's logging, both to STDOUT and to Log Aggregator"""

import json
from unittest import mock
import requests
from mtls_logging import MtlsLogging, Severity


def test_log_stdout_and_mtls(caplog):
    """Ensure any log is sent both to STDOUT and through HTTPS"""
    message = "Message which should appear in both STDOUT and sent as a POST request"
    with_mocked_post(
        send_log, message, Severity.DEBUG, Severity.CRITICAL
    ).assert_called()
    assert message in caplog.text


def test_log_stdout_and_not_mtls(no_log_certs, caplog):
    # pylint: disable=unused-argument
    """Ensure log is only sent to STDOUT when missing log certs"""
    message = "Message which should appear in STDOUT"
    error_message = "Missing TLS logging additional parameter(s): log_ctrl_file app_key app_cert app_cert_file_path"
    with_mocked_post(
        send_log, message, Severity.DEBUG, Severity.CRITICAL
    ).assert_not_called()
    assert message in caplog.text
    assert error_message in caplog.text


def test_log_level_matching_severity(caplog):
    """Ensure a log will output if it matches the severity level of the logger"""
    for severity in Severity:
        message = f"Message sent with severity {severity}, should be logged in STDOUT and through POST"
        with_mocked_post(send_log, message, severity, severity).assert_called()
        assert message in caplog.text


def test_log_ignored(caplog):
    """Ensure that a log will be ignored if we set the minimum severity higher"""
    message = "Message which should appear in both STDOUT and sent as a POST request"
    # This test will still call once because the logger announces its log level as INFO severity
    with_mocked_post(
        send_log, message, Severity.INFO, Severity.DEBUG
    ).assert_called_once()
    assert not message in caplog.text


################################### HELPERS ###################################


def with_mocked_post(log_function, message, logger_level, log_level):
    """Send a log with mocked POST request, ensure the request is called"""
    with mock.patch.object(requests, "post") as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.text = message
        log_function(message, logger_level, log_level)
        return mock_post


def send_log(message, logger_level, log_level):
    """Send a log through the MTLS logger"""
    logger = MtlsLogging(logger_level)
    logger.log(message, log_level)

def test_log_handles_invalid_url(caplog):
    """Ensure logger logs an error if requests.post raises InvalidURL"""
    message = "Test message for InvalidURL"
    with mock.patch.object(requests, "post", side_effect=requests.exceptions.InvalidURL("Bad URL")):
        logger = MtlsLogging(Severity.DEBUG)
        logger.log(message, Severity.CRITICAL)
    assert "Request failed for mTLS logging: Bad URL" in caplog.text


def test_log_handles_missing_schema(caplog):
    """Ensure logger logs an error if requests.post raises MissingSchema"""
    message = "Test message for MissingSchema"
    with mock.patch.object(requests, "post", side_effect=requests.exceptions.MissingSchema("Missing schema")):
        logger = MtlsLogging(Severity.DEBUG)
        logger.log(message, Severity.CRITICAL)
    assert "Request failed for mTLS logging: Missing schema" in caplog.text


def test_init_sets_log_level_from_log_ctrl_file():
    # Sample log control file contents with container mapping
    log_ctrl_data = [
        {"container": "test-container", "severity": "critical"},
        {"container": "other-container", "severity": "warning"},
    ]
    log_ctrl_json = json.dumps(log_ctrl_data)

    # Mocked config dict including the log_ctrl_file path
    mock_config = {
        "log_ctrl_file": "/dummy/path/logcontrol.json",
        "ca_cert_file_name": "ca.pem",
        "ca_cert_file_path": "certs",
        "app_cert": "appcert.pem",
        "app_key": "appkey.pem",
        "app_cert_file_path": "certs",
        "log_endpoint": "log.endpoint"
    }

    # Patch config and environment variable
    with mock.patch("mtls_logging.get_config", return_value=mock_config), \
         mock.patch("mtls_logging.get_os_env_string", return_value="test-container"), \
         mock.patch("builtins.open", mock.mock_open(read_data=log_ctrl_json)):

        logger = MtlsLogging(level=None)
        assert logger.logger.level == Severity.CRITICAL
