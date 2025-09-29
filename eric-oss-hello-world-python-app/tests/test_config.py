"""Tests which cover the app's config"""

from config import get_metrics_namespace

def test_get_metrics_namespace(config):
    assert get_metrics_namespace(config) == "eric_oss_hello_world_python_app"

