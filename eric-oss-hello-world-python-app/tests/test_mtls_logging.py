'''Tests which cover the app's logging, both to STDOUT and to Log Aggregator'''
from unittest import mock
import requests
from mtls_logging import MtlsLogging, Severity


def test_log_stdout_and_mtls(caplog):
    '''Ensure any log is sent both to STDOUT and through HTTPS'''
    message = "Message which should appear in both STDOUT and sent as a POST request"
    with_mocked_post(send_log, message, Severity.DEBUG, Severity.CRITICAL).assert_called()
    assert message in caplog.text

def test_log_stdout_and_not_mtls(no_log_certs, caplog):
    # pylint: disable=unused-argument
    '''Ensure log is only sent to STDOUT when missing log certs'''
    message = "Message which should appear in STDOUT"
    error_message = ("Missing TLS logging additional parameter(s): log_ctrl_file app_key app_cert app_cert_file_path")
    with_mocked_post(send_log, message, Severity.DEBUG, Severity.CRITICAL).assert_not_called()
    assert message in caplog.text
    assert error_message in caplog.text


def test_log_level_matching_severity(caplog):
    '''Ensure a log will output if it matches the severity level of the logger'''
    for severity in Severity:
        message = f"Message sent with severity {severity}, should be logged in STDOUT and through POST"
        with_mocked_post(send_log, message, severity, severity).assert_called()
        assert message in caplog.text


def test_log_ignored(caplog):
    '''Ensure that a log will be ignored if we set the minimum severity higher'''
    message = "Message which should appear in both STDOUT and sent as a POST request"
    # This test will still call once because the logger announces its log level as INFO severity
    with_mocked_post(send_log, message, Severity.INFO, Severity.DEBUG).assert_called_once()
    assert not message in caplog.text


################################### HELPERS ###################################

def with_mocked_post(log_function, message, logger_level, log_level):
    '''Send a log with mocked POST request, ensure the request is called'''
    with mock.patch.object(requests, "post") as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.text = message
        log_function(message, logger_level, log_level)
        return mock_post


def send_log(message, logger_level, log_level):
    '''Send a log through the MTLS logger'''
    logger = MtlsLogging(logger_level)
    logger.log(message, log_level)
