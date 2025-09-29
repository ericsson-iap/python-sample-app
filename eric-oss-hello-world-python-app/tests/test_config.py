"""Tests which cover the app's config"""

from config import get_metrics_namespace

def test_get_metrics_namespace():
    config = {"chosen_name": "chosen-name-for-test"}
    assert get_metrics_namespace(config) == "chosen_name_for_test"
